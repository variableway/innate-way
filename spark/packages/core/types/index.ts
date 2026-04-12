// Shared data types for Spark application

// ─── Ideas ───
export type IdeaStatus = "draft" | "analyzed" | "planned" | "tasked" | "done";
export type IdeaSource = "manual" | "chat" | "clip" | "file" | "feishu";

export interface Idea {
  id: string;
  workspaceId: string;
  title: string;
  content: string;
  source: IdeaSource;
  status: IdeaStatus;
  priority: number;
  tags: string[];
  aiAnalysis?: IdeaAnalysis;
  createdAt: string;
  updatedAt: string;
}

export interface IdeaAnalysis {
  feasibility: "high" | "medium" | "low";
  suggestion: string;
  estimate: string;
  techStack?: string[];
  dependencies?: string[];
}

// ─── Tasks ───
export type TaskStatus =
  | "backlog"
  | "planning"
  | "running"
  | "review"
  | "done"
  | "failed";

export interface Task {
  id: string;
  workspaceId: string;
  parentId?: string;
  ideaId?: string;
  title: string;
  description: string;
  status: TaskStatus;
  priority: number;
  assigneeType?: "human" | "agent";
  assigneeId?: string;
  tags: string[];
  createdAt: string;
  updatedAt: string;
}

// ─── Agents ───
export type AgentStatus =
  | "idle"
  | "working"
  | "blocked"
  | "error"
  | "offline";

export interface Agent {
  id: string;
  name: string;
  provider: string;
  model: string;
  status: AgentStatus;
  skills: string[];
}

// ─── Workspace ───
export interface Workspace {
  id: string;
  name: string;
  description?: string;
  createdAt: string;
  updatedAt: string;
}

// ─── Memory ───
export type MemoryType =
  | "fact"
  | "procedure"
  | "blocker"
  | "reference"
  | "preference";

export interface MemoryEntry {
  id: string;
  workspaceId: string;
  type: MemoryType;
  content: string;
  sourceSessionId?: string;
  createdAt: string;
  updatedAt: string;
}

// ─── Skills ───
export type SkillType = "prompt" | "workflow" | "tool";

export interface Skill {
  id: string;
  workspaceId: string;
  name: string;
  description: string;
  type: SkillType;
  content: string;
  config?: Record<string, unknown>;
  tags: string[];
  version: string;
  source: "built-in" | "marketplace" | "custom";
}

// ─── Chat ───
export type MessageRole = "user" | "assistant" | "tool" | "system";

export interface ChatMessage {
  id: string;
  sessionId: string;
  role: MessageRole;
  content: string;
  toolCalls?: ToolCall[];
  createdAt: string;
}

export interface ToolCall {
  id: string;
  name: string;
  arguments: string;
  result?: string;
}

// ─── Session ───
export interface Session {
  id: string;
  workspaceId: string;
  agentId: string;
  parentSessionId?: string;
  title?: string;
  createdAt: string;
  endedAt?: string;
}
