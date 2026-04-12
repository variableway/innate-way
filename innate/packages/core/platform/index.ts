import type { ChatMessage, Session, Task, Idea, MemoryEntry } from "../types";

// ─── Platform Capabilities ───
export type PlatformCapability =
  | "fs" // File system access
  | "terminal" // Terminal / PTY
  | "local-agent" // Local agent runtime
  | "sidecar" // External process management
  | "tray" // System tray
  | "hotkey" // Global shortcuts
  | "offline" // Offline usage
  | "auto-update"; // Auto update

// ─── Platform Adapters ───
export interface StorageAdapter {
  get(key: string): Promise<string | null>;
  set(key: string, value: string): Promise<void>;
  delete(key: string): Promise<void>;
}

export interface FileSystemAdapter {
  readFile(path: string): Promise<string>;
  writeFile(path: string, content: string): Promise<void>;
  listDir(path: string): Promise<string[]>;
  exists(path: string): Promise<boolean>;
}

export interface TerminalAdapter {
  spawn(
    command: string,
    args: string[],
    options?: { cols?: number; rows?: number }
  ): Promise<string>;
  onOutput(callback: (data: string) => void): void;
  write(data: string): void;
  resize(cols: number, rows: number): void;
  kill(): void;
}

export interface AgentAdapter {
  startSession(agentId: string, prompt: string): Promise<Session>;
  sendMessage(sessionId: string, message: string): Promise<ChatMessage>;
  streamMessage(
    sessionId: string,
    message: string,
    onToken: (token: string) => void
  ): Promise<ChatMessage>;
  endSession(sessionId: string): Promise<void>;
}

export interface NotificationAdapter {
  send(title: string, body: string): Promise<void>;
}

export interface UpdaterAdapter {
  checkForUpdate(): Promise<{ available: boolean; version?: string }>;
  downloadAndInstall(): Promise<void>;
}

// ─── Platform Bridge ───
export interface PlatformAdapter {
  readonly name: "web" | "desktop";
  readonly capabilities: Set<PlatformCapability>;

  // Required
  storage: StorageAdapter;
  agent: AgentAdapter;
  notification: NotificationAdapter;

  // Desktop-only (undefined on web)
  fs?: FileSystemAdapter;
  terminal?: TerminalAdapter;
  updater?: UpdaterAdapter;
}

// ─── Capability Check ───
export function hasCapability(
  platform: PlatformAdapter,
  cap: PlatformCapability
): boolean {
  return platform.capabilities.has(cap);
}

// ─── React Context ───
import { createContext, useContext } from "react";

export const PlatformContext = createContext<PlatformAdapter | null>(null);

export function usePlatform(): PlatformAdapter {
  const platform = useContext(PlatformContext);
  if (!platform) {
    throw new Error("usePlatform must be used within a PlatformProvider");
  }
  return platform;
}

export function useCapability(cap: PlatformCapability): boolean {
  const platform = usePlatform();
  return hasCapability(platform, cap);
}
