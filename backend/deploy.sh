#!/bin/bash

echo "🚀 Deploying AI Code Converter Backend to Fly.io"
echo "================================================"
echo ""

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "❌ Fly CLI not found. Installing..."
    curl -L https://fly.io/install.sh | sh
    echo "✅ Fly CLI installed. Please restart your terminal and run this script again."
    exit 1
fi

# Check if logged in
if ! flyctl auth whoami &> /dev/null; then
    echo "🔐 Please login to Fly.io..."
    flyctl auth login
fi

echo "📦 Deploying application..."
flyctl deploy

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment successful!"
    echo ""
    echo "📝 Next steps:"
    echo "1. Set your API keys:"
    echo "   flyctl secrets set GROQ_API_KEY=your_key_here"
    echo ""
    echo "2. Update CORS origins with your frontend URL:"
    echo "   flyctl secrets set CORS_ORIGINS='http://localhost:5173,https://your-app.vercel.app'"
    echo ""
    echo "3. Test your API:"
    echo "   flyctl open"
    echo ""
    echo "4. View logs:"
    echo "   flyctl logs"
else
    echo ""
    echo "❌ Deployment failed. Check the errors above."
    echo "💡 Try: flyctl logs"
fi
