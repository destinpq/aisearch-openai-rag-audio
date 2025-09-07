"""
Database models and connection handling for user management, folders, and documents.
"""
import os
import hashlib
import jwt
import uuid
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

# PostgreSQL imports
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    logger.warning("psycopg2 not available, falling back to SQLite")
    import sqlite3

# JWT Configuration
JWT_SECRET = os.environ.get("JWT_SECRET", "your-super-secret-jwt-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days

@dataclass
class User:
    id: str
    email: str
    name: str
    password_hash: str
    created_at: datetime
    last_login: Optional[datetime] = None
    avatar: Optional[str] = None

@dataclass
class Folder:
    id: str
    name: str
    user_id: str
    parent_id: Optional[str]
    path: str
    created_at: datetime
    updated_at: datetime
    color: Optional[str] = None
    icon: Optional[str] = None

@dataclass
class Document:
    id: str
    name: str
    original_name: str
    file_type: str
    size: int
    folder_id: str
    user_id: str
    uploaded_at: datetime
    status: str  # 'processing', 'ready', 'error'
    page_count: Optional[int] = None
    text_content: Optional[str] = None
    line_map: Optional[str] = None  # JSON string
    file_path: Optional[str] = None

@dataclass
class Chat:
    id: str
    user_id: str
    session_id: str
    message_type: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    search_mode: str  # 'guarded' or 'unguarded'
    grounding_sources: Optional[str] = None  # JSON string of sources

class Database:
    def __init__(self, db_path: str = "app_data.db"):
        self.db_path = db_path
        self.use_postgres = POSTGRES_AVAILABLE and os.environ.get("USE_POSTGRES", "true").lower() == "true"
        if self.use_postgres:
            self.db_url = os.environ.get("DATABASE_URL", "postgresql://localhost:5432/converse_db")
            logger.info("Using PostgreSQL database")
        else:
            logger.info("Using SQLite database")
        self.init_database()

    def get_connection(self):
        """Get database connection"""
        if self.use_postgres:
            return psycopg2.connect(self.db_url)
        else:
            return sqlite3.connect(self.db_path)

    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                avatar TEXT
            )
        """)

        # Folders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS folders (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                user_id TEXT NOT NULL,
                parent_id TEXT,
                path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                color TEXT,
                icon TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (parent_id) REFERENCES folders(id)
            )
        """)

        # Documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                original_name TEXT NOT NULL,
                file_type TEXT NOT NULL,
                size INTEGER NOT NULL,
                folder_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'processing',
                page_count INTEGER,
                text_content TEXT,
                line_map TEXT,
                file_path TEXT,
                FOREIGN KEY (folder_id) REFERENCES folders(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Chats table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                message_type TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                search_mode TEXT DEFAULT 'unguarded',
                grounding_sources TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_folders_user_id ON folders(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_documents_folder_id ON documents(folder_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chats_user_id ON chats(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chats_session_id ON chats(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chats_timestamp ON chats(timestamp)")
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")

    def get_connection(self):
        """Get database connection with row factory for easier access"""
        if self.use_postgres:
            conn = psycopg2.connect(self.db_url)
            return conn
            return conn
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn

    # User Management
    def create_user(self, email: str, name: str, password: str) -> Optional[User]:
        """Create a new user with hashed password"""
        try:
            user_id = str(uuid.uuid4())
            password_hash = self.hash_password(password)
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO users (id, email, name, password_hash)
                VALUES (?, ?, ?, ?)
            """, (user_id, email, name, password_hash))
            
            conn.commit()
            conn.close()
            
            # Create default root folder for user
            self.create_folder(user_id, "My Documents", None)
            
            return self.get_user_by_id(user_id)
        except sqlite3.IntegrityError:
            logger.warning(f"User with email {email} already exists")
            return None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            
            if row and self.verify_password(password, row['password_hash']):
                # Update last login
                cursor.execute(
                    "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                    (row['id'],)
                )
                conn.commit()
                conn.close()
                
                return User(
                    id=row['id'],
                    email=row['email'],
                    name=row['name'],
                    password_hash=row['password_hash'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    last_login=datetime.fromisoformat(row['last_login']) if row['last_login'] else None,
                    avatar=row['avatar']
                )
            
            conn.close()
            return None
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return User(
                    id=row['id'],
                    email=row['email'],
                    name=row['name'],
                    password_hash=row['password_hash'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    last_login=datetime.fromisoformat(row['last_login']) if row['last_login'] else None,
                    avatar=row['avatar']
                )
            return None
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None

    # Folder Management
    def create_folder(self, user_id: str, name: str, parent_id: Optional[str], color: str = None) -> Optional[Folder]:
        """Create a new folder for a user"""
        try:
            folder_id = str(uuid.uuid4())
            
            # Build path
            if parent_id:
                parent_folder = self.get_folder_by_id(parent_id)
                if not parent_folder or parent_folder.user_id != user_id:
                    return None
                path = f"{parent_folder.path}/{name}"
            else:
                path = f"/{name}"
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO folders (id, name, user_id, parent_id, path, color)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (folder_id, name, user_id, parent_id, path, color))
            
            conn.commit()
            conn.close()
            
            return self.get_folder_by_id(folder_id)
        except Exception as e:
            logger.error(f"Error creating folder: {e}")
            return None

    def get_folders_by_user(self, user_id: str) -> List[Folder]:
        """Get all folders for a user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM folders 
                WHERE user_id = ? 
                ORDER BY path
            """, (user_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            folders = []
            for row in rows:
                folders.append(Folder(
                    id=row['id'],
                    name=row['name'],
                    user_id=row['user_id'],
                    parent_id=row['parent_id'],
                    path=row['path'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                    color=row['color'],
                    icon=row['icon']
                ))
            
            return folders
        except Exception as e:
            logger.error(f"Error getting folders for user: {e}")
            return []

    def get_folder_by_id(self, folder_id: str) -> Optional[Folder]:
        """Get folder by ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM folders WHERE id = ?", (folder_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return Folder(
                    id=row['id'],
                    name=row['name'],
                    user_id=row['user_id'],
                    parent_id=row['parent_id'],
                    path=row['path'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                    color=row['color'],
                    icon=row['icon']
                )
            return None
        except Exception as e:
            logger.error(f"Error getting folder by ID: {e}")
            return None

    # Document Management
    def create_document(self, name: str, original_name: str, file_type: str, size: int,
                       folder_id: str, user_id: str, text_content: str = None,
                       line_map: str = None, page_count: int = None,
                       file_path: str = None) -> Optional[Document]:
        """Create a new document record"""
        try:
            document_id = str(uuid.uuid4())
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO documents (id, name, original_name, file_type, size, folder_id, 
                                     user_id, text_content, line_map, page_count, file_path, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ready')
            """, (document_id, name, original_name, file_type, size, folder_id, user_id,
                  text_content, line_map, page_count, file_path))
            
            conn.commit()
            conn.close()
            
            return self.get_document_by_id(document_id)
        except Exception as e:
            logger.error(f"Error creating document: {e}")
            return None

    def get_documents_by_user(self, user_id: str, folder_id: str = None) -> List[Document]:
        """Get documents for a user, optionally filtered by folder"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if folder_id:
                cursor.execute("""
                    SELECT * FROM documents 
                    WHERE user_id = ? AND folder_id = ?
                    ORDER BY uploaded_at DESC
                """, (user_id, folder_id))
            else:
                cursor.execute("""
                    SELECT * FROM documents 
                    WHERE user_id = ?
                    ORDER BY uploaded_at DESC
                """, (user_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            documents = []
            for row in rows:
                documents.append(Document(
                    id=row['id'],
                    name=row['name'],
                    original_name=row['original_name'],
                    file_type=row['file_type'],
                    size=row['size'],
                    folder_id=row['folder_id'],
                    user_id=row['user_id'],
                    uploaded_at=datetime.fromisoformat(row['uploaded_at']),
                    status=row['status'],
                    page_count=row['page_count'],
                    text_content=row['text_content'],
                    line_map=row['line_map'],
                    file_path=row['file_path']
                ))
            
            return documents
        except Exception as e:
            logger.error(f"Error getting documents for user: {e}")
            return []

    def get_document_by_id(self, document_id: str) -> Optional[Document]:
        """Get document by ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM documents WHERE id = ?", (document_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return Document(
                    id=row['id'],
                    name=row['name'],
                    original_name=row['original_name'],
                    file_type=row['file_type'],
                    size=row['size'],
                    folder_id=row['folder_id'],
                    user_id=row['user_id'],
                    uploaded_at=datetime.fromisoformat(row['uploaded_at']),
                    status=row['status'],
                    page_count=row['page_count'],
                    text_content=row['text_content'],
                    line_map=row['line_map'],
                    file_path=row['file_path']
                )
            return None
        except Exception as e:
            logger.error(f"Error getting document by ID: {e}")
            return None

    # Chat Management
    def save_chat_message(self, user_id: str, session_id: str, message_type: str, content: str, 
                         search_mode: str = 'unguarded', grounding_sources: Optional[List[Dict[str, Any]]] = None) -> Optional[Chat]:
        """Save a chat message"""
        try:
            chat_id = str(uuid.uuid4())
            grounding_sources_json = json.dumps(grounding_sources) if grounding_sources else None
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO chats (id, user_id, session_id, message_type, content, search_mode, grounding_sources)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (chat_id, user_id, session_id, message_type, content, search_mode, grounding_sources_json))
            
            conn.commit()
            conn.close()
            
            return self.get_chat_by_id(chat_id)
        except Exception as e:
            logger.error(f"Error saving chat message: {e}")
            return None

    def get_chat_by_id(self, chat_id: str) -> Optional[Chat]:
        """Get chat message by ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM chats WHERE id = ?", (chat_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return Chat(
                    id=row['id'],
                    user_id=row['user_id'],
                    session_id=row['session_id'],
                    message_type=row['message_type'],
                    content=row['content'],
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    search_mode=row['search_mode'],
                    grounding_sources=row['grounding_sources']
                )
            return None
        except Exception as e:
            logger.error(f"Error getting chat by ID: {e}")
            return None

    def get_chat_history(self, user_id: str, session_id: Optional[str] = None, limit: int = 50) -> List[Chat]:
        """Get chat history for a user, optionally filtered by session"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if session_id:
                cursor.execute("""
                    SELECT * FROM chats 
                    WHERE user_id = ? AND session_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (user_id, session_id, limit))
            else:
                cursor.execute("""
                    SELECT * FROM chats 
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (user_id, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            chats = []
            for row in rows:
                chats.append(Chat(
                    id=row['id'],
                    user_id=row['user_id'],
                    session_id=row['session_id'],
                    message_type=row['message_type'],
                    content=row['content'],
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    search_mode=row['search_mode'],
                    grounding_sources=row['grounding_sources']
                ))
            
            return chats
        except Exception as e:
            logger.error(f"Error getting chat history: {e}")
            return []

    def get_chat_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get distinct chat sessions for a user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT session_id, MAX(timestamp) as last_message, COUNT(*) as message_count
                FROM chats 
                WHERE user_id = ?
                GROUP BY session_id
                ORDER BY last_message DESC
            """, (user_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            sessions = []
            for row in rows:
                sessions.append({
                    'session_id': row['session_id'],
                    'last_message': datetime.fromisoformat(row['last_message']),
                    'message_count': row['message_count']
                })
            
            return sessions
        except Exception as e:
            logger.error(f"Error getting chat sessions: {e}")
            return []

    def search_documents(self, user_id: str, query: str, folder_ids: List[str] = None) -> List[Dict[str, Any]]:
        """Search documents by text content for a specific user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Base query
            sql = """
                SELECT d.*, f.name as folder_name 
                FROM documents d
                JOIN folders f ON d.folder_id = f.id
                WHERE d.user_id = ? AND d.text_content LIKE ?
            """
            params = [user_id, f"%{query}%"]
            
            # Add folder filter if specified
            if folder_ids:
                placeholders = ",".join("?" * len(folder_ids))
                sql += f" AND d.folder_id IN ({placeholders})"
                params.extend(folder_ids)
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            conn.close()
            
            results = []
            for row in rows:
                # Find line matches within the document
                text_content = row['text_content'] or ""
                lines = text_content.split('\n')
                matches = []
                
                for i, line in enumerate(lines, 1):
                    if query.lower() in line.lower():
                        matches.append({
                            'lineNumber': i,
                            'text': line.strip(),
                            'context': self._get_line_context(lines, i-1, 2)
                        })
                
                if matches:
                    results.append({
                        'documentId': row['id'],
                        'documentName': row['name'],
                        'folderName': row['folder_name'],
                        'matches': matches
                    })
            
            return results
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []

    def _get_line_context(self, lines: List[str], line_idx: int, context_size: int = 2) -> str:
        """Get context around a specific line"""
        start = max(0, line_idx - context_size)
        end = min(len(lines), line_idx + context_size + 1)
        context_lines = lines[start:end]
        return '\n'.join(context_lines)

    # Authentication helpers
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return hashlib.sha256(password.encode()).hexdigest() == hashed

    # JWT Token Management
    def generate_jwt_token(self, user: User) -> str:
        """Generate JWT token for user"""
        payload = {
            'user_id': user.id,
            'email': user.email,
            'name': user.name,
            'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    @staticmethod
    def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None

# Global database instance
db = Database()
