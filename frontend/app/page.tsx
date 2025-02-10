'use client';

import Link from 'next/link';
import { Button } from "@/components/ui/button";
import {
  ArrowRight,
  Building2,
  BarChart3,
  MessageSquare,
  Search,
  DollarSign,
  LineChart,
  Building,
  ChevronRight,
} from "lucide-react";
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import { GradientText } from '@/components/ui/gradient-text';
import { HeroPattern } from '@/components/ui/hero-pattern';
import { FeatureCard } from '@/components/ui/feature-card';

const features = [
  {
    icon: Building2,
    title: "Property Analysis",
    description: "Get detailed insights into property characteristics, value potential, and market position with our advanced AI analysis."
  },
  {
    icon: BarChart3,
    title: "Market Research",
    description: "Access comprehensive market data, trends analysis, and predictive insights to make informed investment decisions."
  },
  {
    icon: MessageSquare,
    title: "AI Chat Assistant",
    description: "Engage with our intelligent assistant for real-time support, market insights, and property analysis guidance."
  },
  {
    icon: Search,
    title: "Smart Search",
    description: "Utilize our powerful search capabilities to find and analyze properties, market data, and investment opportunities."
  },
  {
    icon: DollarSign,
    title: "Financial Tools",
    description: "Calculate ROI, analyze cash flows, and evaluate investment scenarios with our suite of financial analysis tools."
  },
  {
    icon: LineChart,
    title: "Performance Tracking",
    description: "Monitor and analyze investment performance with real-time tracking and detailed reporting capabilities."
  }
];

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-background">
      {/* <Navbar /> */}
      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative isolate pt-24 lg:pt-36 pb-24">
          <HeroPattern />
          <div className="mx-auto max-w-7xl px-6 lg:px-8">
            <div className="mx-auto max-w-2xl text-center">
              <h1 className="text-4xl font-bold tracking-tight sm:text-6xl lg:text-7xl">
                Intelligent{' '}
                <GradientText 
                  animate 
                  from="from-blue-600"
                  to="to-blue-400"
                  direction="ltr"
                  className="inline-block"
                >
                  Commercial Real Estate
                </GradientText>
                {' '}Analysis
              </h1>
              <p className="mt-6 text-lg leading-8 text-muted-foreground">
                Transform your commercial real estate decisions with AI-powered insights.
                Get instant property analysis, market research, and investment recommendations.
              </p>
              <div className="mt-10 flex items-center justify-center gap-x-6">
                <Link href="/chat">
                  <Button size="lg" className="gap-2">
                    Start Analyzing
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </Link>
                
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="relative isolate py-24 sm:py-32">
          <div className="mx-auto max-w-7xl px-6 lg:px-8">
            <div className="mx-auto max-w-2xl text-center">
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
                Everything you need to analyze and manage your real estate investments
              </h2>
              <p className="mt-6 text-lg leading-8 text-muted-foreground">
                Our comprehensive suite of tools helps you make data-driven decisions
                and maximize your investment potential.
              </p>
            </div>

            <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
              <div className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-16 lg:max-w-none lg:grid-cols-3">
                {features.map((feature) => (
                  <FeatureCard
                    key={feature.title}
                    icon={feature.icon}
                    title={feature.title}
                    description={feature.description}
                  />
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="relative isolate py-24 sm:py-32">
          <div className="mx-auto max-w-7xl px-6 lg:px-8">
            <div className="mx-auto max-w-2xl text-center">
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
                Ready to transform your real estate analysis?
              </h2>
              <p className="mt-6 text-lg leading-8 text-muted-foreground">
                Join thousands of real estate professionals who are already using our AI-powered platform
                to make smarter investment decisions.
              </p>
              <div className="mt-10 flex items-center justify-center gap-x-6">
                <Link href="/chat">
                  <Button size="lg" className="gap-2">
                    Get Started
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}