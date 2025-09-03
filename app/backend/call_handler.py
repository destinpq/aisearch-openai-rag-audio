import os
import logging
from typing import Dict, Any
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
from azure.core.credentials import AzureKeyCredential
from azure.identity import AzureDeveloperCliCredential, DefaultAzureCredential

from ragtools import attach_rag_tools
from rtmt import RTMiddleTier

logger = logging.getLogger("voicerag-calling")

class CallHandler:
    def __init__(self):
        # Twilio client
        self.twilio_client = Client(
            os.environ.get("TWILIO_ACCOUNT_SID"),
            os.environ.get("TWILIO_AUTH_TOKEN")
        )
        self.twilio_phone_number = os.environ.get("TWILIO_PHONE_NUMBER")

        # Azure credentials
        llm_key = os.environ.get("AZURE_OPENAI_API_KEY")
        search_key = os.environ.get("AZURE_SEARCH_API_KEY")

        credential = None
        if not llm_key or not search_key:
            if tenant_id := os.environ.get("AZURE_TENANT_ID"):
                logger.info("Using AzureDeveloperCliCredential with tenant_id %s", tenant_id)
                credential = AzureDeveloperCliCredential(tenant_id=tenant_id, process_timeout=60)
            else:
                logger.info("Using DefaultAzureCredential")
                credential = DefaultAzureCredential()

        llm_credential = AzureKeyCredential(llm_key) if llm_key else credential
        search_credential = AzureKeyCredential(search_key) if search_key else credential

        # RTMT for voice processing
        self.rtmt = RTMiddleTier(
            credentials=llm_credential,
            endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            deployment=os.environ["AZURE_OPENAI_REALTIME_DEPLOYMENT"],
            voice_choice=os.environ.get("AZURE_OPENAI_REALTIME_VOICE_CHOICE") or "alloy"
        )

        self.rtmt.system_message = """
            You are a helpful assistant answering questions about company policies and procedures.
            Only answer questions based on information you searched in the knowledge base.
            Keep answers concise and clear for phone conversations.
            Always use the 'search' tool to check the knowledge base before answering.
            If the answer isn't in the knowledge base, say you don't know.
        """.strip()

        attach_rag_tools(self.rtmt,
            credentials=search_credential,
            search_endpoint=os.environ.get("AZURE_SEARCH_ENDPOINT"),
            search_index=os.environ.get("AZURE_SEARCH_INDEX"),
            semantic_configuration=os.environ.get("AZURE_SEARCH_SEMANTIC_CONFIGURATION") or None,
            identifier_field=os.environ.get("AZURE_SEARCH_IDENTIFIER_FIELD") or "chunk_id",
            content_field=os.environ.get("AZURE_SEARCH_CONTENT_FIELD") or "chunk",
            embedding_field=os.environ.get("AZURE_SEARCH_EMBEDDING_FIELD") or "text_vector",
            title_field=os.environ.get("AZURE_SEARCH_TITLE_FIELD") or "title",
            use_vector_query=(os.getenv("AZURE_SEARCH_USE_VECTOR_QUERY", "true") == "true")
        )

        # Store active calls
        self.active_calls: Dict[str, Dict[str, Any]] = {}

    def generate_twiml_response(self, call_sid: str, user_input: str = None) -> str:
        """Generate TwiML response for the call"""
        response = VoiceResponse()

        if not user_input:
            # Initial greeting
            response.say("Hello! I'm your AI assistant. How can I help you today?", voice='alice')
            response.gather(
                input='speech',
                action='/call/twiml',
                method='POST',
                speech_timeout='auto',
                speech_model='phone_call'
            )
        else:
            # Process user input and generate response
            try:
                # Here we would process the speech input through RTMT
                # For now, we'll use a simple response
                ai_response = self._process_user_input(user_input)

                response.say(ai_response, voice='alice')
                response.gather(
                    input='speech',
                    action='/call/twiml',
                    method='POST',
                    speech_timeout='auto',
                    speech_model='phone_call'
                )
            except Exception as e:
                logger.error(f"Error processing user input: {e}")
                response.say("I'm sorry, I encountered an error. Please try again.", voice='alice')
                response.gather(
                    input='speech',
                    action='/call/twiml',
                    method='POST',
                    speech_timeout='auto',
                    speech_model='phone_call'
                )

        return str(response)

    def _process_user_input(self, user_input: str) -> str:
        """Process user speech input and generate AI response"""
        # This is a simplified version - in production you'd integrate with RTMT
        # For now, return a basic response
        if "policy" in user_input.lower():
            return "I can help you with company policies. What specific policy are you looking for?"
        elif "benefit" in user_input.lower():
            return "I can assist with benefits information. What would you like to know?"
        else:
            return "I'm here to help with company information. Could you please be more specific?"

    def initiate_call(self, to_number: str) -> Dict[str, Any]:
        """Initiate an outbound call"""
        try:
            call = self.twilio_client.calls.create(
                to=to_number,
                from_=self.twilio_phone_number,
                url=f"{os.environ.get('BASE_URL', 'http://localhost:8765')}/call/twiml",
                method='POST'
            )

            self.active_calls[call.sid] = {
                'to': to_number,
                'status': call.status,
                'start_time': call.start_time
            }

            return {
                'success': True,
                'call_sid': call.sid,
                'status': call.status
            }
        except Exception as e:
            logger.error(f"Error initiating call: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_call_status(self, call_sid: str) -> Dict[str, Any]:
        """Get the status of a call"""
        try:
            call = self.twilio_client.calls(call_sid).fetch()
            return {
                'call_sid': call.sid,
                'status': call.status,
                'duration': call.duration,
                'start_time': call.start_time,
                'end_time': call.end_time
            }
        except Exception as e:
            logger.error(f"Error getting call status: {e}")
            return {
                'error': str(e)
            }

    def end_call(self, call_sid: str) -> Dict[str, Any]:
        """End an active call"""
        try:
            call = self.twilio_client.calls(call_sid).update(status='completed')
            if call_sid in self.active_calls:
                del self.active_calls[call_sid]
            return {
                'success': True,
                'status': call.status
            }
        except Exception as e:
            logger.error(f"Error ending call: {e}")
            return {
                'success': False,
                'error': str(e)
            }
