"use client";

import { useEffect, useState, type ReactNode } from "react";
import Link from "next/link";
import { useSession, signOut } from "next-auth/react";
import { brandsApi, Brand, mockupsApi, MockupResponse, userApi, UsageResponse } from "@/lib/api";
import { Loader2, Sparkles, BarChart, Shield, LogOut, ArrowRight, AlertCircle } from "lucide-react";

export default function DashboardPage() {
  const { data: session, status } = useSession();
  const [usage, setUsage] = useState<UsageResponse | null>(null);
  const [mockups, setMockups] = useState<MockupResponse[]>([]);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (status === "authenticated") {
      loadData();
    }
  }, [status]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [usageResp, mockupResp, brandResp] = await Promise.all([
        userApi.usage(),
        mockupsApi.list(),
        brandsApi.list().catch(() => []),
      ]);
      setUsage(usageResp);
      setMockups(mockupResp.slice(0, 6));
      setBrands(brandResp.slice(0, 3));
    } catch (err: any) {
      setError(err?.message || "Failed to load dashboard");
    } finally {
      setLoading(false);
    }
  };

  if (status === "loading" || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-violet-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-violet-600" />
            <span className="font-bold text-xl text-gray-900">MockupAI Dashboard</span>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/generate" className="text-sm text-violet-600 font-medium hover:underline">
              Generate
            </Link>
            <Link href="/brands" className="text-sm text-gray-600 hover:text-gray-900">
              Brands
            </Link>
            <button
              onClick={() => signOut({ callbackUrl: "/login" })}
              className="flex items-center gap-2 px-3 py-2 border rounded-lg text-gray-700 hover:bg-gray-100"
            >
              <LogOut className="w-4 h-4" />
              Sign out
            </button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 space-y-6">
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg flex items-center gap-2">
            <AlertCircle className="w-4 h-4" />
            {error}
          </div>
        )}

        <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <UsageCard
            title="Tier"
            value={session?.tier?.toUpperCase() || "FREE"}
            secondary={usage ? `Resets: ${usage.resets_at ? new Date(usage.resets_at).toLocaleDateString() : "monthly"}` : ""}
            icon={<Shield className="w-5 h-5" />}
          />
          <UsageCard
            title="Mockups"
            value={usage?.counts?.mockups_generated ?? 0}
            secondary={
              usage?.limits?.mockups_generated
                ? `Limit ${usage.limits.mockups_generated}`
                : "Unlimited"
            }
            icon={<BarChart className="w-5 h-5" />}
          />
          <UsageCard
            title="Exports"
            value={usage?.counts?.exports ?? 0}
            secondary={
              usage?.limits?.exports ? `Limit ${usage.limits.exports}` : "Unlimited"
            }
            icon={<BarChart className="w-5 h-5" />}
          />
        </section>

        {usage && usage.tier !== "agency" && (
          <div className="p-4 bg-gradient-to-r from-violet-600 to-indigo-600 text-white rounded-xl flex items-center justify-between">
            <div>
              <p className="font-semibold">Upgrade for higher limits</p>
              <p className="text-sm text-violet-100">Pro and Agency tiers unlock more mockups, exports, and team seats.</p>
            </div>
            <button className="flex items-center gap-2 px-4 py-2 bg-white text-violet-700 rounded-lg shadow">
              Upgrade (coming soon)
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}

        <section className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white rounded-xl border p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-gray-900">Recent Mockups</h3>
              <Link href="/generate" className="text-sm text-violet-600 hover:underline">
                View all
              </Link>
            </div>
            {mockups.length === 0 ? (
              <p className="text-sm text-gray-500">No mockups yet.</p>
            ) : (
              <div className="grid grid-cols-3 gap-2">
                {mockups.map((m) => (
                  <img
                    key={m.id}
                    src={m.image_url}
                    alt="Mockup"
                    className="rounded-lg border object-cover aspect-square"
                  />
                ))}
              </div>
            )}
          </div>

          <div className="bg-white rounded-xl border p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-gray-900">Brands</h3>
              <Link href="/brands" className="text-sm text-violet-600 hover:underline">
                Manage
              </Link>
            </div>
            {brands.length === 0 ? (
              <p className="text-sm text-gray-500">Create a brand to keep styling consistent.</p>
            ) : (
              <div className="space-y-2">
                {brands.map((b) => (
                  <div key={b.id} className="flex items-center justify-between border rounded-lg px-3 py-2">
                    <div>
                      <p className="font-medium text-gray-900">{b.name}</p>
                      <p className="text-xs text-gray-500 capitalize">{b.industry || "Brand"}</p>
                    </div>
                    {b.is_default && (
                      <span className="text-xs px-2 py-1 rounded-full bg-violet-100 text-violet-700">
                        Default
                      </span>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}

function UsageCard({
  title,
  value,
  secondary,
  icon,
}: {
  title: string;
  value: string | number;
  secondary?: string;
  icon: ReactNode;
}) {
  return (
    <div className="bg-white border rounded-xl p-4 shadow-sm flex items-center gap-3">
      <div className="p-3 rounded-lg bg-violet-50 text-violet-700">{icon}</div>
      <div>
        <p className="text-sm text-gray-500">{title}</p>
        <p className="text-xl font-semibold text-gray-900">{value}</p>
        {secondary && <p className="text-xs text-gray-500">{secondary}</p>}
      </div>
    </div>
  );
}

