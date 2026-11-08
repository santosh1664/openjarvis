import { useEffect, useMemo, useState } from 'react';

type AgentState = 'working' | 'waiting' | 'complete' | 'idle';

type OfficeAgent = {
  id: string;
  name: string;
  role: string;
  task: string;
  state: AgentState;
  accent: string;
};

const initialAgents: OfficeAgent[] = [
  { id: 'planner', name: 'Planner', role: 'Task planning', task: 'Breaking request into steps', state: 'working', accent: '#22d3ee' },
  { id: 'builder', name: 'Builder', role: 'Implementation', task: 'Waiting for a task', state: 'idle', accent: '#a78bfa' },
  { id: 'reviewer', name: 'Reviewer', role: 'Quality & safety', task: 'Monitoring approvals', state: 'waiting', accent: '#fbbf24' },
  { id: 'memory', name: 'Memory', role: 'Knowledge', task: 'Indexing local context', state: 'working', accent: '#34d399' },
];

const cycle: Array<{ state: AgentState; task: string }> = [
  { state: 'working', task: 'Processing task context' },
  { state: 'working', task: 'Executing bounded step' },
  { state: 'waiting', task: 'Waiting for approval' },
  { state: 'complete', task: 'Step completed' },
];

function stateLabel(state: AgentState) {
  return { working: 'WORKING', waiting: 'WAITING', complete: 'DONE', idle: 'IDLE' }[state];
}

function stateColor(state: AgentState) {
  return { working: 'var(--color-accent)', waiting: 'var(--color-accent-amber)', complete: 'var(--color-success)', idle: 'var(--color-text-tertiary)' }[state];
}

export function OfficeFloor() {
  const [agents, setAgents] = useState(initialAgents);
  const [tick, setTick] = useState(0);

  useEffect(() => {
    const timer = window.setInterval(() => setTick((value) => value + 1), 2200);
    return () => window.clearInterval(timer);
  }, []);

  const liveAgents = useMemo(
    () => agents.map((agent, index) => {
      if (agent.state === 'idle') return agent;
      const next = cycle[(tick + index) % cycle.length];
      return { ...agent, ...next };
    }),
    [agents, tick],
  );

  useEffect(() => {
    const onAgentEvent = (event: Event) => {
      const detail = (event as CustomEvent<Partial<OfficeAgent> & { id: string }>).detail;
      if (!detail?.id) return;
      setAgents((current) => current.map((agent) => agent.id === detail.id ? { ...agent, ...detail } : agent));
    };
    window.addEventListener('jarvis:agent-update', onAgentEvent);
    return () => window.removeEventListener('jarvis:agent-update', onAgentEvent);
  }, []);

  return (
    <section className="rounded-xl border p-4 mb-4 overflow-hidden" style={{ borderColor: 'var(--color-border)', background: 'var(--color-surface)' }} aria-label="JARVIS office floor">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h2 className="text-sm font-semibold" style={{ color: 'var(--color-text)' }}>JARVIS Office Floor</h2>
          <p className="text-xs mt-1" style={{ color: 'var(--color-text-secondary)' }}>Realtime agent activity and task progress</p>
        </div>
        <span className="flex items-center gap-1.5 text-[10px] uppercase tracking-widest" style={{ color: 'var(--color-success)' }}>
          <span className="h-2 w-2 rounded-full animate-pulse" style={{ background: 'var(--color-success)' }} /> LIVE
        </span>
      </div>

      <div className="relative rounded-lg p-3 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3" style={{ background: 'linear-gradient(135deg, var(--color-bg-secondary), var(--color-bg-tertiary))' }}>
        <div className="absolute inset-0 opacity-30 pointer-events-none" style={{ backgroundImage: 'linear-gradient(var(--color-border) 1px, transparent 1px), linear-gradient(90deg, var(--color-border) 1px, transparent 1px)', backgroundSize: '28px 28px' }} />
        {liveAgents.map((agent) => (
          <article key={agent.id} className="relative rounded-lg border p-3 transition-all duration-500" style={{ borderColor: agent.state === 'working' ? agent.accent : 'var(--color-border)', background: 'color-mix(in srgb, var(--color-surface) 88%, transparent)', boxShadow: agent.state === 'working' ? `0 0 18px ${agent.accent}22` : 'none' }}>
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-center gap-2">
                <div className={agent.state === 'working' ? 'animate-bounce' : ''} style={{ fontSize: 22 }} role="img" aria-label={`${agent.name} avatar`}>▣</div>
                <div>
                  <div className="text-xs font-semibold" style={{ color: 'var(--color-text)' }}>{agent.name}</div>
                  <div className="text-[10px]" style={{ color: 'var(--color-text-tertiary)' }}>{agent.role}</div>
                </div>
              </div>
              <span className="text-[9px] font-mono" style={{ color: stateColor(agent.state) }}>{stateLabel(agent.state)}</span>
            </div>
            <div className="mt-3 text-[11px] truncate" style={{ color: 'var(--color-text-secondary)' }}>{agent.task}</div>
            <div className="mt-2 h-1 rounded-full overflow-hidden" style={{ background: 'var(--color-bg-tertiary)' }}>
              <div className={agent.state === 'working' ? 'h-full transition-all duration-700 animate-pulse' : 'h-full transition-all duration-700'} style={{ width: agent.state === 'complete' ? '100%' : agent.state === 'waiting' ? '68%' : agent.state === 'working' ? '42%' : '8%', background: agent.accent }} />
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
