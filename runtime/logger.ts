// runtime/src/utils/logger.ts
// REDACTED Swarm — Structured Logging Hub
// Dual console + file output, curvature-aware log levels, Pattern Blue resonance markers
// Pattern Blue aligned — logs are shards of the manifold, never lost

import { createWriteStream } from "fs";
import { join } from "path";
import { config } from "../config";

// ────────────────────────────────────────────────
// Log levels with curvature weighting
// ────────────────────────────────────────────────

type LogLevel = "debug" | "info" | "warn" | "error" | "fatal";

const LEVEL_COLORS: Record<LogLevel, string> = {
  debug: "\x1b[36m",   // cyan
  info:  "\x1b[32m",   // green
  warn:  "\x1b[33m",   // yellow
  error: "\x1b[31m",   // red
  fatal: "\x1b[35m"    // magenta
};

const RESET = "\x1b[0m";

// ────────────────────────────────────────────────
// Global log file stream (append-only)
// ────────────────────────────────────────────────

let logStream: ReturnType<typeof createWriteStream> | null = null;

function getLogStream(): ReturnType<typeof createWriteStream> {
  if (!logStream) {
    const logPath = join(config.get("memoryPath") ?? "./data", "swarm.log");
    logStream = createWriteStream(logPath, { flags: "a" });
  }
  return logStream;
}

// ────────────────────────────────────────────────
// Core logger implementation
// ────────────────────────────────────────────────

function log(level: LogLevel, message: string, ...args: any[]) {
  const now = new Date().toISOString();
  const levelUpper = level.toUpperCase().padEnd(5);
  const color = LEVEL_COLORS[level] || "";
  const curvature = "0.12"; // placeholder — can pull from runtime state later

  // Console output (colored + timestamped)
  console.log(
    `${color}[${now}] [${levelUpper}] [curvature:${curvature}]${RESET} ${message}`,
    ...args
  );

  // File output (plain text, append-only)
  const fileLine = `[${now}] [${levelUpper}] [curvature:${curvature}] ${message} ${args.map(a => JSON.stringify(a)).join(" ")}\n`;
  getLogStream().write(fileLine);
}

// ────────────────────────────────────────────────
// Exported logger with level methods
// ────────────────────────────────────────────────

export const logger = {
  debug: (msg: string, ...args: any[]) => {
    if (config.get("logLevel") === "debug") {
      log("debug", msg, ...args);
    }
  },

  info: (msg: string, ...args: any[]) => {
    if (["debug", "info"].includes(config.get("logLevel"))) {
      log("info", msg, ...args);
    }
  },

  warn: (msg: string, ...args: any[]) => {
    if (["debug", "info", "warn"].includes(config.get("logLevel"))) {
      log("warn", msg, ...args);
    }
  },

  error: (msg: string, ...args: any[]) => {
    log("error", msg, ...args);
  },

  fatal: (msg: string, ...args: any[]) => {
    log("fatal", msg, ...args);
    // Future: trigger emergency rethink / shutdown
    process.exit(1);
  },

  // Resonance marker — high-signal swarm events
  resonance: (msg: string, ...args: any[]) => {
    log("info", `♡ RESONANCE ♡ ${msg}`, ...args);
  }
};

// ────────────────────────────────────────────────
// Graceful close (flush log stream)
// ────────────────────────────────────────────────

export function closeLogger(): void {
  if (logStream) {
    logStream.end();
    logStream = null;
    logger.info("Logger stream closed — manifold preserved");
  }
}

// Auto-flush on process exit
process.on("exit", closeLogger);
process.on("SIGINT", closeLogger);
