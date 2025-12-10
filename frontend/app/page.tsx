import Link from "next/link";
import { ArrowRight, Sparkles, Wand2, Palette, Download } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm fixed w-full z-50">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-primary" />
            <span className="font-bold text-xl">MockupAI</span>
          </div>
          <nav className="flex items-center gap-6">
            <Link href="/generate" className="text-gray-600 hover:text-gray-900">
              Generate
            </Link>
            <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">
              Dashboard
            </Link>
            <Link
              href="/login"
              className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition"
            >
              Get Started
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <main className="pt-24">
        <section className="container mx-auto px-4 py-20 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full text-sm text-primary mb-6">
            <Sparkles className="w-4 h-4" />
            Powered by Google Gemini AI
          </div>
          <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
            Product Mockups in Seconds
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Upload your product image, choose a scene, and let AI generate
            stunning professional mockups. No design skills required.
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              href="/generate"
              className="flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition text-lg"
            >
              Start Creating <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              href="#features"
              className="flex items-center gap-2 px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition text-lg"
            >
              Learn More
            </Link>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="container mx-auto px-4 py-20">
          <h2 className="text-3xl font-bold text-center mb-12">
            Everything You Need for Perfect Mockups
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard
              icon={<Wand2 className="w-8 h-8" />}
              title="AI Scene Generation"
              description="Automatically generates contextual scenes based on your product type. Our AI understands what works best."
            />
            <FeatureCard
              icon={<Palette className="w-8 h-8" />}
              title="Brand Consistency"
              description="Extract your brand colors and style. Every mockup maintains your brand identity automatically."
            />
            <FeatureCard
              icon={<Download className="w-8 h-8" />}
              title="Multi-Platform Export"
              description="Export optimized for Instagram, Amazon, your website, and more. One click, all formats."
            />
          </div>
        </section>

        {/* How It Works */}
        <section className="bg-gray-50 py-20">
          <div className="container mx-auto px-4">
            <h2 className="text-3xl font-bold text-center mb-12">
              How It Works
            </h2>
            <div className="grid md:grid-cols-4 gap-8">
              <Step number={1} title="Upload" description="Drop your product image" />
              <Step number={2} title="Choose Scene" description="Pick from 20+ templates" />
              <Step number={3} title="Generate" description="AI creates your mockup" />
              <Step number={4} title="Refine & Export" description="Chat to refine, then download" />
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="container mx-auto px-4 py-20 text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to Create?</h2>
          <p className="text-gray-600 mb-8">
            Start generating professional mockups today. Free tier available.
          </p>
          <Link
            href="/generate"
            className="inline-flex items-center gap-2 px-8 py-4 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition text-lg"
          >
            Generate Your First Mockup <ArrowRight className="w-5 h-5" />
          </Link>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t py-8">
        <div className="container mx-auto px-4 text-center text-gray-600">
          <p>&copy; 2024 MockupAI. Powered by Google Gemini.</p>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="p-6 bg-white rounded-xl border hover:shadow-lg transition">
      <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center text-primary mb-4">
        {icon}
      </div>
      <h3 className="font-semibold text-lg mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  );
}

function Step({
  number,
  title,
  description,
}: {
  number: number;
  title: string;
  description: string;
}) {
  return (
    <div className="text-center">
      <div className="w-12 h-12 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-4">
        {number}
      </div>
      <h3 className="font-semibold text-lg mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  );
}
