#!/bin/bash

# Domain Setup Demo for PDF RAG Platform
echo "🌐 PDF RAG Platform - Domain Configuration Demo"
echo "=============================================="

echo
echo "📋 Why Use a Domain Instead of Localhost?"
echo "----------------------------------------"
echo "✅ Professional appearance and branding"
echo "✅ SSL/HTTPS security for production"
echo "✅ Multiple subdomains for different services"
echo "✅ Better SEO and marketing"
echo "✅ Proper CORS configuration"
echo "✅ Email notifications from proper domain"
echo "✅ Payment processing requires HTTPS"
echo "✅ Mobile app integration"

echo
echo "🎯 Recommended Domain Structure:"
echo "------------------------------"
echo "Main Site:     https://pdfrag.ai"
echo "User App:      https://app.pdfrag.ai"
echo "API Server:    https://api.pdfrag.ai" 
echo "Admin Panel:   https://admin.pdfrag.ai"
echo "Documentation: https://docs.pdfrag.ai"
echo "Status Page:   https://status.pdfrag.ai"
echo "File Storage:  https://files.pdfrag.ai"

echo
echo "💰 Suggested Domain Names (Check Availability):"
echo "-----------------------------------------------"
domains=(
    "pdfrag.ai"
    "docrag.com"
    "aipdfreader.com"
    "smartpdfrag.com"
    "pdfanalyzer.ai"
    "ragpdf.com"
    "pdfdocs.ai"
    "intelligentpdf.com"
    "pdfinsights.ai"
    "documentrag.com"
)

for domain in "${domains[@]}"; do
    echo "• $domain"
done

echo
echo "🚀 Quick Production Setup:"
echo "-------------------------"
echo "1. Purchase domain (e.g., pdfrag.ai)"
echo "2. Point DNS to your server IP"
echo "3. Set environment variables:"
echo "   export DOMAIN=pdfrag.ai"
echo "   export PRODUCTION=true"
echo "4. Run: ./deploy_production.sh"
echo "5. SSL certificates auto-configured"

echo
echo "🔧 Testing with Custom Domain:"
echo "-----------------------------"
echo "You can test domain functionality locally by:"
echo "1. Edit /etc/hosts:"
echo "   127.0.0.1 pdfrag.local"
echo "   127.0.0.1 app.pdfrag.local"
echo "   127.0.0.1 api.pdfrag.local"
echo
echo "2. Set environment:"
echo "   export DOMAIN=pdfrag.local"
echo "   export PRODUCTION=false"
echo
echo "3. Access via:"
echo "   http://app.pdfrag.local:52047/login"

echo
echo "💡 Current Status:"
echo "-----------------"
if [ "$DOMAIN" ]; then
    echo "✅ Domain configured: $DOMAIN"
    if [ "$PRODUCTION" = "true" ]; then
        echo "✅ Production mode enabled"
        echo "🌐 App URL: https://app.$DOMAIN"
        echo "🔌 API URL: https://api.$DOMAIN"
    else
        echo "🔧 Development mode (localhost)"
        echo "🌐 App URL: http://localhost:52047/dashboard"
        echo "🔌 API URL: http://localhost:52047/api"
    fi
else
    echo "🔧 Using localhost (development mode)"
    echo "💡 Set DOMAIN environment variable for production"
fi

echo
echo "📞 Next Steps:"
echo "-------------"
echo "1. Choose and purchase a domain"
echo "2. Configure DNS records"
echo "3. Run production deployment script"
echo "4. Test the complete user flow"
echo "5. Set up monitoring and backups"

echo
echo "🎉 Your service-based PDF RAG platform will be production-ready!"
