import { spawn } from "node:child_process";
import path from "node:path";
import { Plugin } from "@opencode/plugin";

interface RunSlopResult {
  stdout: string;
  stderr: string;
  exitCode: number;
}

export default Plugin.define({
  id: "sloperator.run-slop",
  setup: async (ctx) => {
    const projectRoot = ctx.location.project.directory;

    await ctx.tool.transform((tools) => {
      tools.add({
        name: "run_slop",
        description:
          "Run a SlopLang (.slop) program with Sloperator. Returns the program's stdout, stderr, and exit code.",
        input: {
          type: "object",
          properties: {
            path: {
              type: "string",
              description:
                "Path to the .slop file, relative to the project root or absolute.",
            },
          },
          required: ["path"],
          additionalProperties: false,
        },
        output: {
          type: "object",
          properties: {
            stdout: { type: "string" },
            stderr: { type: "string" },
            exitCode: { type: "number" },
          },
          required: ["stdout", "stderr", "exitCode"],
          additionalProperties: false,
        },
        options: { codemode: false },
        execute: async (input) => {
          const { path: file } = input as { path: string };
          const resolved = path.isAbsolute(file)
            ? file
            : path.resolve(projectRoot, file);

          const result = await new Promise<RunSlopResult>((resolve) => {
            const child = spawn(
              "uv",
              ["run", "--no-active", "sloperator.py", resolved],
              {
                cwd: projectRoot,
                stdio: ["ignore", "pipe", "pipe"],
              },
            );

            let stdout = "";
            let stderr = "";

            child.stdout.setEncoding("utf8");
            child.stderr.setEncoding("utf8");
            child.stdout.on("data", (chunk: string) => {
              stdout += chunk;
            });
            child.stderr.on("data", (chunk: string) => {
              stderr += chunk;
            });
            child.on("error", (error) => {
              resolve({
                stdout,
                stderr: stderr ? `${stderr}\n${String(error)}` : String(error),
                exitCode: -1,
              });
            });
            child.on("close", (code) => {
              resolve({ stdout, stderr, exitCode: code ?? -1 });
            });
          });

          return {
            output: result,
            content: JSON.stringify(result, null, 2),
          };
        },
      });
    });
  },
});
