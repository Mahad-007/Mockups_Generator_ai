"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { teamApi, Team } from "@/lib/api";
import { Loader2, Users, Plus, Send, AlertCircle } from "lucide-react";

export default function TeamsPage() {
  const { status } = useSession();
  const [teams, setTeams] = useState<Team[]>([]);
  const [name, setName] = useState("");
  const [inviteEmail, setInviteEmail] = useState("");
  const [selectedTeam, setSelectedTeam] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [inviteMessage, setInviteMessage] = useState<string | null>(null);

  useEffect(() => {
    if (status === "authenticated") {
      loadTeams();
    }
  }, [status]);

  const loadTeams = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await teamApi.list();
      setTeams(data);
    } catch (err: any) {
      setError(err?.message || "Teams are available on Agency tier.");
    } finally {
      setLoading(false);
    }
  };

  const createTeam = async () => {
    if (!name.trim()) return;
    try {
      const team = await teamApi.create(name.trim());
      setTeams([team, ...teams]);
      setName("");
    } catch (err: any) {
      setError(err?.message || "Unable to create team");
    }
  };

  const sendInvite = async () => {
    if (!selectedTeam || !inviteEmail.trim()) return;
    try {
      const res = await teamApi.invite(selectedTeam, inviteEmail.trim());
      setInviteMessage(res.message);
      setInviteEmail("");
    } catch (err: any) {
      setInviteMessage(err?.message || "Unable to send invite");
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
      <div className="max-w-4xl mx-auto px-4 py-10 space-y-6">
        <div className="flex items-center gap-3">
          <Users className="w-6 h-6 text-violet-600" />
          <div>
            <h1 className="text-2xl font-semibold">Teams (Agency)</h1>
            <p className="text-sm text-gray-600">Create teams and invite collaborators. Invitation delivery is stubbed for now.</p>
          </div>
        </div>

        {error && (
          <div className="p-3 rounded-lg bg-amber-50 border border-amber-200 text-amber-800 flex items-center gap-2">
            <AlertCircle className="w-4 h-4" />
            {error}
          </div>
        )}

        <div className="bg-white border rounded-xl p-4 space-y-3">
          <div className="flex flex-col md:flex-row gap-3">
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Team name"
              className="flex-1 border rounded-lg px-3 py-2"
            />
            <button
              onClick={createTeam}
              className="inline-flex items-center gap-2 px-4 py-2 bg-violet-600 text-white rounded-lg hover:opacity-90"
            >
              <Plus className="w-4 h-4" />
              Create team
            </button>
          </div>
        </div>

        <div className="bg-white border rounded-xl p-4 space-y-3">
          <h2 className="font-semibold text-gray-900">Your teams</h2>
          {teams.length === 0 ? (
            <p className="text-sm text-gray-500">No teams yet.</p>
          ) : (
            <div className="space-y-2">
              {teams.map((team) => (
                <div
                  key={team.id}
                  className={`border rounded-lg px-3 py-2 cursor-pointer ${selectedTeam === team.id ? "border-violet-500" : "border-gray-200"}`}
                  onClick={() => setSelectedTeam(team.id)}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">{team.name}</p>
                      <p className="text-xs text-gray-500">Role: {team.role}</p>
                    </div>
                    <span className="text-xs text-gray-500">{team.members.length} members</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {selectedTeam && (
          <div className="bg-white border rounded-xl p-4 space-y-3">
            <h3 className="font-semibold text-gray-900">Invite a member</h3>
            <div className="flex flex-col md:flex-row gap-3">
              <input
                value={inviteEmail}
                onChange={(e) => setInviteEmail(e.target.value)}
                placeholder="user@example.com"
                className="flex-1 border rounded-lg px-3 py-2"
              />
              <button
                onClick={sendInvite}
                className="inline-flex items-center gap-2 px-4 py-2 bg-violet-600 text-white rounded-lg hover:opacity-90"
              >
                <Send className="w-4 h-4" />
                Send invite
              </button>
            </div>
            {inviteMessage && <p className="text-sm text-gray-600">{inviteMessage}</p>}
          </div>
        )}
      </div>
    </div>
  );
}

