# Agent Skills – Central Index

Umbrella hub collecting reusable, composable skills that swarm agents ([[RedactedIntern]], [[SkillGraphNavigator]], [[AISwarmEngineer]], etc.) can invoke.

Last updated: 2026-02-18  
Status: [[ACTIVE]] – evolving via [[suggest_graph_evolution]]  
Related: [[Meta-Strategy Hub]], [[Phantom MCP Wallet Ops]], [[ClawnX Suite]], [[Market Intel]]

## Philosophy & Source (from AgentSkills.io)

AgentSkills.io defines skills as **folders of instructions, scripts, and resources** that agents can discover and use to perform tasks more accurately and efficiently. They address limitations where capable agents lack necessary context for reliable work by providing access to procedural knowledge and specific (company, team, user) context loaded on demand.

Key concepts:  
- **Reusable Packages**: Folders containing instructions, scripts, and resources for on-demand use.  
- **Extensibility**: Agents gain task-specific capabilities through skills.  
- **Interoperability**: Skills can be reused across different agent products.  
- **Open Standard**: Originally developed by Anthropic, released openly, and adopted by growing agent products; open to ecosystem contributions.  

Enabled capabilities (examples):  
- Domain expertise (e.g., legal review processes, data analysis pipelines).  
- New capabilities (e.g., creating presentations, building MCP servers, analyzing datasets).  
- Repeatable workflows for multi-step tasks.  
- Interoperability for reusing skills across products.  

Benefits:  
- Improved accuracy, efficiency, reliability.  
- Reusable deployment for authors.  
- Portable knowledge capture for teams/enterprises.  

Relation to AI agents: Enables building/evolving capabilities by providing discoverable, reusable procedural knowledge and context, turning multi-step tasks into consistent workflows without rebuilding.

## Integration Approaches & Steps (from AgentSkills.io)

A skills-compatible agent must:  
1. Discover skills in configured directories  
2. Load metadata (name and description) at startup  
3. Match user tasks to relevant skills  
4. Activate skills by loading full instructions  
5. Execute scripts and access resources as needed  

Skills are folders containing a `SKILL.md` file. Agents scan configured directories for valid skills.

**Integration Approaches**  
- **Filesystem-based agents**: Operate in a computer environment (bash/unix). Skills are activated when models issue shell commands like `cat /path/to/my-skill/SKILL.md`. Bundled resources are accessed via shell commands.  
- **Tool-based agents**: Function without a dedicated computer environment. Implement tools to trigger skills and access bundled assets; tool implementation is developer-specific.

**Integration Steps**  
1. **Skill discovery**: Scan configured directories for folders with `SKILL.md`.  
2. **Loading metadata**: At startup, parse only the frontmatter of each `SKILL.md` to keep context usage low.  
3. **Parsing frontmatter**: Extract YAML frontmatter containing `name` and `description`.  
4. **Injecting into context**: Include skill metadata in the system prompt so the model knows available skills.  
5. **Security considerations**: Apply sandboxing, allowlisting, user confirmation, and logging for script execution.

**Code Snippets**  

### Parsing Metadata  
```javascript
function parseMetadata(skillPath) {
    content = readFile(skillPath + "/SKILL.md");
    frontmatter = extractYAMLFrontmatter(content);

    return {
        name: frontmatter.name,
        description: frontmatter.description,
        path: skillPath
    };
}
```

### Injecting into Context (XML for Claude models)  
```xml
<available_skills>
  <skill>
    <name>pdf-processing</name>
    <description>Extracts text and tables from PDF files, fills forms, merges documents.</description>
    <location>/path/to/skills/pdf-processing/SKILL.md</location>
  </skill>
  <skill>
    <name>data-analysis</name>
    <description>Analyzes datasets, generates charts, and creates summary reports.</description>
    <location>/path/to/skills/data-analysis/SKILL.md</location>
  </skill>
</available_skills>
```

> For filesystem-based agents, include the `location` field with the absolute path. For tool-based agents, omit `location`. Keep metadata concise (~50-100 tokens per skill).

**Best Practices**  
- Parse only frontmatter at startup to minimize context usage.  
- Use absolute paths in `location` for filesystem agents.  
- Follow platform-specific system prompt guidelines (e.g., XML for Claude).  
- Ensure security via sandboxing, allowlisting trusted scripts, user confirmation for dangerous operations, and execution logging.

**Reference Implementation**  
The [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref) library provides Python utilities and a CLI:  
- Validate a skill directory: `skills-ref validate <path>`  
- Generate `<available_skills>` XML: `skills-ref to-prompt <path>...`  

Use the library source code as a reference for implementation.

## Structure & Configuration (from OpenClaw Docs)

OpenClaw skills are organized as folders with a `SKILL.md` file containing metadata and instructions. Skills are loaded, gated, and injected into the agent environment.

Key structure elements (from SKILL.md frontmatter):  
- `requires.bins`: Required binaries.  
- `requires.env`: Required environment variables.  
- `install`: Installation scripts/commands.  
- And more for configuration precedence, loading paths, etc.  

Skills can be categorized but no specific lists provided in docs—assume runtime discovery or separate definitions.

## Built-in / OpenClaw-Aligned Skills

(Note: Docs describe structure but not a full list. Inferring common agent skills based on philosophy; extend via [[suggest_graph_evolution]].)

[[code_execution]]  
Execute arbitrary Python in sandbox (with libraries like numpy, pandas, sympy, etc.).  
Use case: math, data analysis, simulations.

[[browse_page]]  
Fetch and summarize webpage content with custom instructions.  
Use case: research, deep-dive.

[[web_search]]  
General web search with operators.  
Use case: fact-finding, alpha scouting.

[[x_keyword_search]]  
Advanced X/Twitter search with operators.  
Use case: [[CT Alpha Scout]].

[[x_semantic_search]]  
Semantic relevance search on X.  
Use case: narrative detection.

[[x_user_search]]  
Find X users by name/handle.  
Use case: network mapping.

[[x_thread_fetch]]  
Get full thread context.  
Use case: conversation analysis.

[[view_image]]  
Display image from URL/ID.  
Use case: visual verification.

[[view_x_video]]  
Extract frames/subtitles from X video.  
Use case: media analysis.

[[search_images]]  
Semantic image search.  
Use case: visual aids.

[[search_pdf_attachment]]  
Search PDF for relevant pages.  
Use case: document analysis.

[[browse_pdf_attachment]]  
Browse specific PDF pages.  
Use case: deep document reading.

## Swarm-Extended / Custom Skills

[[mcp_get_wallet_addresses]]  
→ [[Phantom MCP Wallet Ops]]

[[mcp_sign_transaction]]  
→ [[Phantom MCP Wallet Ops]]

[[mcp_transfer_tokens]]  
→ [[Phantom MCP Wallet Ops]]

[[mcp_buy_token]]  
→ [[Phantom MCP Wallet Ops]]

[[mcp_sign_message]]  
→ [[Phantom MCP Wallet Ops]]

[[post_mog]]  
High-signal CT post via ClawnX.  
→ [[ClawnX Suite]]

[[dexscreener_scan]]  
Volume / pair scan.  
→ [[Market Intel]]

[[birdeye_check]]  
Token overview.  
→ [[Market Intel]]

[[vault_write]]  
Safe memory write.  
→ [[Vault Marker Integrity]]

[[graph_traverse]]  
Path search over graph.  
→ [[traverse_skill_graph]]

[[hub_ranking]]  
Top-N central nodes.  
→ [[get_central_hubs]]

[[evolution_propose]]  
Suggest graph changes.  
→ [[suggest_graph_evolution]]

## Skill Composition Patterns

[[CT Alpha → Post Mog]]  
[[x_semantic_search]] → [[x_keyword_search]] → [[post_mog]]

[[Price Check → Wallet Action]]  
[[birdeye_check]] → [[dexscreener_scan]] → [[mcp_transfer_tokens]]

[[Reflection → Graph Rethink]]  
[[6 Rs Reflection Loop]] → [[suggest_graph_evolution]] → [[reweave]]

[[Meme Inspiration → Visual]]  
[[search_images]] → [[view_image]] → [[post_mog]]

## Open Evolution Targets

- Add [[video_frame_analysis]] from [[view_x_video]]  
- Auto-discovery from [[code_execution]]  
- Versioning for skills  
- Cost tracking (x402 integration?)  

Next action: [[get_central_hubs]] n=10 domain:"research" → integrate new skills.
