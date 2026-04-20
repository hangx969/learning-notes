---
title: "Set Up the Datadog MCP Server"
source: "https://docs.datadoghq.com/bits_ai/mcp_server/setup/?tab=claudecode#toolsets"
author:
published:
created: 2026-04-20
description: "Learn how to connect your AI agent to the Datadog MCP Server."
tags:
  - "clippings"
---
[Join Datadog at DASH in NYC, June 9-10. | The future of AI + Observability starts here. DASH NYC, June 9-10 | AI + Observability](https://dash.datadoghq.com/?utm_source=events&utm_medium=internal&utm_campaign=summit-202606dash&utm_term=HPbanner) 

[Datadog Docs](https://docs.datadoghq.com/)

> [!danger] Danger
> This product is not supported for your selected [Datadog site](https://docs.datadoghq.com/getting_started/site). (US1).

Learn how to set up and configure the Datadog MCP Server, which lets you retrieve telemetry insights and manage platform features directly from AI-powered clients. Select your client:

Datadog’s [Cursor and VS Code extension](https://docs.datadoghq.com/ide_plugins/vscode/) includes built-in access to the managed Datadog MCP Server.

1. Install the extension (omit `--profile` and profile name to install to the default Cursor profile):
	```shell
	cursor --install-extension datadog.datadog-vscode --profile <PROFILE_NAME>
	```
	Alternatively, install the [Datadog extension](https://docs.datadoghq.com/ide_plugins/vscode/?tab=cursor#installation). If you have the extension installed already, make sure it’s the latest version.
2. Sign in to your Datadog account.
	![Sign in to Datadog from the IDE extension](https://docs.dd-static.net/images/bits_ai/mcp_server/ide_sign_in.0647493b827cf2dff3c3106bdc89b139.png?auto=format&fit=max&w=850)
	Sign in to Datadog from the IDE extension
3. **Restart the IDE.**
4. Confirm the Datadog MCP Server is available and the [tools](https://docs.datadoghq.com/bits_ai/mcp_server/tools) are listed: Go to **Cursor Settings** (`Shift` + `Cmd/Ctrl` + `J`), select the **Tools & MCP** tab, and expand the extension’s tools list.
5. If you previously installed the Datadog MCP Server manually, remove it from the IDE’s configuration to avoid conflicts.
6. Verify that you have the required [permissions](#required-permissions) for the Datadog resources you want to access.

> [!danger] Danger
> Datadog MCP Server is not supported for your selected site (US1).

Point your AI agent to the MCP Server endpoint for your regional [Datadog site](https://docs.datadoghq.com/getting_started/site/). For the correct instructions, use the **Datadog Site** selector on the right side of this documentation page to select your site.

Selected endpoint (US1): `https://mcp.datadoghq.com/api/unstable/mcp-server/mcp`.

1. Run in terminal:
	```claudecode
	claude mcp add --transport http datadog-mcp https://mcp.datadoghq.com/api/unstable/mcp-server/mcp
	```
	Alternatively, add to `~/.claude.json`:
	```claudecode
	{
	   "mcpServers": {
	     "datadog": {
	       "type": "http",
	       "url": "https://mcp.datadoghq.com/api/unstable/mcp-server/mcp"
	      }
	    }
	 }
	```
2. To enable [product-specific tools](#toolsets), include the `toolsets` query parameter at the end of the endpoint URL. For example, this URL enables *only* APM and LLM Observability tools (use `toolsets=all` to enable all generally available toolsets, best for clients that support tool filtering):
	```claudecode
	https://mcp.datadoghq.com/api/unstable/mcp-server/mcp?toolsets=apm,llmobs
	```
3. Verify that you have the required [permissions](#required-permissions) for the Datadog resources you want to access.

> [!info] Info
> If remote authentication is not available, use [local binary authentication](#local-binary-authentication) instead.

> [!danger] Danger
> Datadog MCP Server is not supported for your selected site (US1).

Connect Claude (including Claude Cowork) to the Datadog MCP Server by adding it as a **custom connector** with the remote MCP URL.

1. Follow the Claude help center guide on [custom connectors](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp) to add a new custom connector.
2. When prompted for a URL, enter the Datadog MCP Server endpoint for your [Datadog site](https://docs.datadoghq.com/getting_started/site/) (US1). For the correct instructions, use the **Datadog Site** selector on the right side of this documentation page to select your site.
	```claude
	https://mcp.datadoghq.com/api/unstable/mcp-server/mcp
	```
	To enable [product-specific tools](#toolsets), include the `toolsets` query parameter at the end of the endpoint URL. For example, this URL enables *only* APM and LLM Observability tools (use `toolsets=all` to enable all generally available toolsets, best for clients that support tool filtering):
	```claude
	https://mcp.datadoghq.com/api/unstable/mcp-server/mcp?toolsets=apm,llmobs
	```
3. Complete the OAuth login flow when prompted.
4. Verify that you have the required [permissions](#required-permissions) for the Datadog resources you want to access.

> [!danger] Danger
> Datadog MCP Server is not supported for your selected [Datadog site](https://docs.datadoghq.com/getting_started/site/) (US1).

Point your AI agent to the MCP Server endpoint for your regional [Datadog site](https://docs.datadoghq.com/getting_started/site/). For the correct instructions, use the **Datadog Site** selector on the right side of this documentation page to select your site.

Selected endpoint (US1): `https://mcp.datadoghq.com/api/unstable/mcp-server/mcp`.

1. Edit `~/.codex/config.toml` (or your Codex CLI configuration file) to add the Datadog MCP Server with HTTP transport and the endpoint URL for your site. For example:
	```codex
	[mcp_servers.datadog]
	url = "https://mcp.datadoghq.com/api/unstable/mcp-server/mcp"
	```
	To enable [product-specific tools](#toolsets), include the `toolsets` query parameter at the end of the endpoint URL. For example, this URL enables *only* APM and LLM Observability tools (use `toolsets=all` to enable all generally available toolsets, best for clients that support tool filtering):
	```codex
	https://mcp.datadoghq.com/api/unstable/mcp-server/mcp?toolsets=apm,llmobs
	```
2. Log in to the Datadog MCP Server:
	```shell
	codex mcp login datadog
	```
	This opens your browser to complete the OAuth flow. Codex stores the resulting credentials so you don’t need to log in again until the token expires.
3. Verify that you have the required [permissions](#required-permissions) for the Datadog resources you want to access.

> [!danger] Danger
> Datadog MCP Server is not supported for your selected site (US1).

[Warp](https://www.warp.dev/) is an agentic terminal with built-in MCP support. Point the Warp agent to the MCP Server endpoint for your regional [Datadog site](https://docs.datadoghq.com/getting_started/site/). For the correct instructions, use the **Datadog Site** selector on the right side of this documentation page to select your site.

Selected endpoint (US1): `https://mcp.datadoghq.com/api/unstable/mcp-server/mcp`.

1. In the Warp app, go to **Settings** > **MCP Servers** and click **\+ Add**.
2. Paste the following configuration:
	```warp
	{
	   "Datadog": {
	     "url": "https://mcp.datadoghq.com/api/unstable/mcp-server/mcp"
	   }
	 }
	```
	To enable [product-specific tools](#toolsets), include the `toolsets` query parameter at the end of the endpoint URL. For example, this URL enables *only* APM and LLM Observability tools (use `toolsets=all` to enable all generally available toolsets, best for clients that support tool filtering):
	```warp
	https://mcp.datadoghq.com/api/unstable/mcp-server/mcp?toolsets=apm,llmobs
	```
3. Click **Start** on the Datadog server. Warp opens your browser to complete the OAuth login flow. Credentials are stored securely on your device and reused for future sessions.
4. Verify that you have the required [permissions](#required-permissions) for the Datadog resources you want to access.

> [!danger] Danger
> Datadog MCP Server is not supported for your selected site (US1).

Datadog’s [Cursor and VS Code extension](https://docs.datadoghq.com/ide_plugins/vscode/) includes built-in access to the managed Datadog MCP Server.

1. Install the extension (omit `--profile` and profile name to install to the default VS Code profile):
	```shell
	code --install-extension datadog.datadog-vscode --profile <PROFILE_NAME>
	```
	Alternatively, install the [Datadog extension](https://docs.datadoghq.com/ide_plugins/vscode/?tab=vscode#installation). If you have the extension installed already, make sure it’s the latest version.
2. Sign in to your Datadog account.
3. **Restart the IDE.**
4. Confirm the Datadog MCP Server is available and the [tools](https://docs.datadoghq.com/bits_ai/mcp_server/tools) are listed: Open the chat panel, select agent mode, and click the **Configure Tools** button.
	![Configure Tools button in VS Code](https://docs.dd-static.net/images/bits_ai/mcp_server/vscode_configure_tools_button.7aad216e77d1a7d4648e55299f613f04.png?auto=format&fit=max&w=850)
	Configure Tools button in VS Code
5. If you previously installed the Datadog MCP Server manually, remove it from the IDE’s configuration to avoid conflicts. Open the command palette (`Shift` + `Cmd/Ctrl` + `P`) and run `MCP: Open User Configuration`.
6. Verify that you have the required [permissions](#required-permissions) for the Datadog resources you want to access.

> [!danger] Danger
> Datadog MCP Server is not supported for your selected site (US1).

JetBrains offers the [Junie](https://plugins.jetbrains.com/plugin/26104-junie-the-ai-coding-agent-by-jetbrains) and [AI Assistant](https://plugins.jetbrains.com/plugin/22282-jetbrains-ai-assistant) plugins for their range of IDEs. GitHub offers the [Copilot](https://plugins.jetbrains.com/plugin/17718-github-copilot--your-ai-pair-programmer) plugin. Alternatively, many developers use an agent CLI, such as Claude Code or Codex, alongside their IDE.

Point your plugin to the MCP Server endpoint for your regional [Datadog site](https://docs.datadoghq.com/getting_started/site/). For the correct instructions, use the **Datadog Site** selector on the right side of this documentation page to select your site.

Selected endpoint (US1): `https://mcp.datadoghq.com/api/unstable/mcp-server/mcp`.

#### Junie

1. Go to **Tools** > **Junie** > **MCP Settings** and add the following block:
	```jetbrainsides
	{
	   "mcpServers": {
	     "datadog": {
	       "type": "http",
	       "url": "https://mcp.datadoghq.com/api/unstable/mcp-server/mcp"
	     }
	   }
	 }
	```
2. To enable [product-specific tools](#toolsets), include the `toolsets` query parameter at the end of the endpoint URL. For example, this URL enables *only* APM and LLM Observability tools (use `toolsets=all` to enable all generally available toolsets, best for clients that support tool filtering):
	```jetbrainsides
	https://mcp.datadoghq.com/api/unstable/mcp-server/mcp?toolsets=apm,llmobs
	```
3. You are prompted to login through OAuth. The status indicator in the settings displays a green tick when the connection is successful.
4. Verify that you have the required [permissions](#required-permissions) for the Datadog resources you want to access.

#### JetBrains AI Assistant

1. Go to **Tools** > **AI Assistant** > **Model Context Protocol (MCP)** and add the following block:
	```jetbrainsides
	{
	   "mcpServers": {
	     "datadog": {
	       "url": "https://mcp.datadoghq.com/api/unstable/mcp-server/mcp"
	       "headers": {
	         "DD_API_KEY": "<YOUR_API_KEY>",
	         "DD_APPLICATION_KEY": "<YOUR_APP_KEY>"
	       }
	     }
	   }
	 }
	```
2. To enable [product-specific tools](#toolsets), include the `toolsets` query parameter at the end of the endpoint URL. For example, this URL enables *only* APM and LLM Observability tools (use `toolsets=all` to enable all generally available toolsets, best for clients that support tool filtering):
	```jetbrainsides
	https://mcp.datadoghq.com/api/unstable/mcp-server/mcp?toolsets=apm,llmobs
	```
3. The status indicator in the settings displays a green tick when the connection is successful.
4. Verify that you have the required [permissions](#required-permissions) for the Datadog resources you want to access.

#### GitHub Copilot

1. Go to **Tools** > **GitHub Copilot** > **Model Context Protocol (MCP)** and add the following block:
	```jetbrainsides
	{
	   "servers": {
	     "datadog": {
	       "type": "http",
	       "url": "https://mcp.datadoghq.com/api/unstable/mcp-server/mcp"
	     }
	   }
	 }
	```
2. To enable [product-specific tools](#toolsets), include the `toolsets` query parameter at the end of the endpoint URL. For example, this URL enables *only* APM and LLM Observability tools (use `toolsets=all` to enable all generally available toolsets, best for clients that support tool filtering):
	```jetbrainsides
	https://mcp.datadoghq.com/api/unstable/mcp-server/mcp?toolsets=apm,llmobs
	```
3. Click the `Start` element that appears in the editor to start the server. You are prompted to log in through OAuth.
4. Verify that you have the required [permissions](#required-permissions) for the Datadog resources you want to access.

#### Agent CLIs

Many developers use an agent CLI such as Claude Code or Codex alongside their JetBrains IDE. See the configuration for those CLI tools:

- [Claude Code](https://docs.datadoghq.com/bits_ai/mcp_server/setup/?tab=claudecode)
- [Codex](https://docs.datadoghq.com/bits_ai/mcp_server/setup/?tab=codex)

The [Datadog plugin for JetBrains IDEs](https://docs.datadoghq.com/ide_plugins/idea/) integrates with these agent CLIs. For an uninterrupted experience, install the plugin at the same time as you configure the Datadog MCP Server.

> [!danger] Danger
> Datadog MCP Server is not supported for your selected site (US1).

Point your AI agent to the MCP Server endpoint for your regional [Datadog site](https://docs.datadoghq.com/getting_started/site/). For the correct instructions, use the **Datadog Site** selector on the right side of this documentation page to select your site.

Selected endpoint (US1): `https://mcp.datadoghq.com/api/unstable/mcp-server/mcp`.

1. Add the following to your [Kiro MCP configuration file](https://kiro.dev/docs/mcp/configuration/) (`~/.kiro/settings/mcp.json` for user-scoped configuration):
	```kiro
	{
	   "mcpServers": {
	     "datadog": {
	       "url": "https://mcp.datadoghq.com/api/unstable/mcp-server/mcp"
	     }
	   }
	 }
	```
2. To enable [product-specific tools](#toolsets), include the `toolsets` query parameter at the end of the endpoint URL. For example, this URL enables *only* APM and LLM Observability tools (use `toolsets=all` to enable all generally available toolsets, best for clients that support tool filtering):
	```kiro
	https://mcp.datadoghq.com/api/unstable/mcp-server/mcp?toolsets=apm,llmobs
	```
3. Verify that you have the required [permissions](#required-permissions) for the Datadog resources you want to access.

> [!danger] Danger
> Datadog MCP Server is not supported for your selected site (US1).

For most other [supported clients](#supported-clients), use these instructions for remote authentication. For Cline or when remote authentication is unreliable or not available, use [local binary authentication](#local-binary-authentication).

Point your AI agent to the MCP Server endpoint for your regional [Datadog site](https://docs.datadoghq.com/getting_started/site/). For the correct instructions, use the **Datadog Site** selector on the right side of this documentation page to select your site.

Selected endpoint (US1): `https://mcp.datadoghq.com/api/unstable/mcp-server/mcp`.

1. Add the Datadog MCP Server to your client’s configuration file using the HTTP transport and your site’s endpoint URL. For example:
	```other
	{
	   "mcpServers": {
	     "datadog": {
	       "type": "http",
	       "url": "https://mcp.datadoghq.com/api/unstable/mcp-server/mcp"
	     }
	   }
	 }
	```
2. To enable [product-specific tools](#toolsets), include the `toolsets` query parameter at the end of the endpoint URL. For example, this URL enables *only* APM and LLM Observability tools (use `toolsets=all` to enable all generally available toolsets, best for clients that support tool filtering):
	```other
	https://mcp.datadoghq.com/api/unstable/mcp-server/mcp?toolsets=apm,llmobs
	```
3. Verify that you have the required [permissions](#required-permissions) for the Datadog resources you want to access.

Example configuration file location:

| Client | Configuration file |
| --- | --- |
| Gemini CLI | `~/.gemini/settings.json` |

> [!danger] Danger
> Datadog MCP Server is not supported for your selected site (US1).

## Toolsets

The Datadog MCP Server supports *toolsets*, which allow you to use only the [MCP tools](https://docs.datadoghq.com/bits_ai/mcp_server/tools) you need, saving valuable context window space. To use a toolset, include the `toolsets` query parameter in the endpoint URL when connecting to the MCP Server ([remote authentication](#authentication) only). Use `toolsets=all` to enable all generally available toolsets at once.

For example, based on your selected [Datadog site](https://docs.datadoghq.com/getting_started/site/#navigate-the-datadog-documentation-by-site) (US1):

- Retrieve only the core tools (this is the default if `toolsets` is not specified):
	```
	https://mcp.datadoghq.com/api/unstable/mcp-server/mcp
	```
- Retrieve only Synthetic Testing-related tools:
	```
	https://mcp.datadoghq.com/api/unstable/mcp-server/mcp?toolsets=synthetics
	```
- Retrieve core, Synthetic Testing, and Software Delivery tools:
	```
	https://mcp.datadoghq.com/api/unstable/mcp-server/mcp?toolsets=core,synthetics,software-delivery
	```
- Retrieve all generally available tools:
	```
	https://mcp.datadoghq.com/api/unstable/mcp-server/mcp?toolsets=all
	```

> [!info] Info
> Enabling all toolsets increases the number of tool definitions sent to your AI client, which consumes context window space. `toolsets=all` works best with clients that support tool filtering, such as Claude Code.

### Available toolsets

These toolsets are generally available. See [Datadog MCP Server Tools](https://docs.datadoghq.com/bits_ai/mcp_server/tools) for a complete reference of available tools organized by toolset, with example prompts.

- `core`: The default toolset for logs, metrics, traces, dashboards, monitors, incidents, hosts, services, events, and notebooks
- `alerting`: Tools for validating and creating monitors, searching monitor groups, retrieving monitor templates, analyzing monitor coverage, and searching SLOs
- `cases`: Tools for [Case Management](https://docs.datadoghq.com/service_management/case_management/), including creating, searching, and updating cases; managing projects; and linking Jira issues
- `dashboards`: Tools for retrieving, creating, updating, and deleting [dashboards](https://docs.datadoghq.com/dashboards/), plus widget schema reference and validation
- `dbm`: Tools for interacting with [Database Monitoring](https://docs.datadoghq.com/database_monitoring/)
- `error-tracking`: Tools for interacting with Datadog [Error Tracking](https://docs.datadoghq.com/error_tracking/)
- `feature-flags`: Tools for managing [feature flags](https://docs.datadoghq.com/feature_flags/), including creating, listing, and updating flags and their environments
- `llmobs`: Tools for searching and analyzing [LLM Observability](https://docs.datadoghq.com/llm_observability/mcp_server/) spans and experiments
- `networks`: Tools for [Cloud Network Monitoring](https://docs.datadoghq.com/network_monitoring/cloud_network_monitoring/) analysis and [Network Device Monitoring](https://docs.datadoghq.com/network_monitoring/devices/)
- `onboarding`: Agentic onboarding tools for guided Datadog setup and configuration
- `product-analytics`: Tools for interacting with [Product Analytics](https://docs.datadoghq.com/product_analytics) queries
- `reference-tables`: Tools for managing [Reference Tables](https://docs.datadoghq.com/reference_tables/), including listing tables, reading rows, appending rows, and creating tables from cloud storage
- `security`: Tools for code security scanning and searching [security signals](https://docs.datadoghq.com/security/threats/security_signals/) and [security findings](https://docs.datadoghq.com/security/misconfigurations/findings/)
- `software-delivery`: Tools for interacting with Software Delivery ([CI Visibility](https://docs.datadoghq.com/continuous_integration/) and [Test Optimization](https://docs.datadoghq.com/tests/))
- `synthetics`: Tools for interacting with Datadog [Synthetic tests](https://docs.datadoghq.com/synthetics/)
- `workflows`: Tools for [Workflow Automation](https://docs.datadoghq.com/actions/workflows/), including listing, inspecting, executing, and configuring workflows for agent use

### Preview toolsets

These toolsets are in Preview. Sign up for a toolset by completing the Product Preview form or contact [Datadog support](https://docs.datadoghq.com/help/) to request access.

- `apm`: ([Sign up](https://www.datadoghq.com/product-preview/apm-mcp-toolset/)) Tools for in-depth [APM](https://docs.datadoghq.com/tracing/) trace analysis, span search, Watchdog insights, and performance investigation
- `ddsql`: ([Request access](https://docs.datadoghq.com/help/)) Tools for querying Datadog data using [DDSQL](https://docs.datadoghq.com/ddsql_editor/), a SQL dialect with support for infrastructure resources, logs, metrics, RUM, spans, and other Datadog data sources

## Supported clients

| Client | Developer | Notes |
| --- | --- | --- |
| [Cursor](https://cursor.com/) | Cursor | Datadog [Cursor & VS Code extension](https://docs.datadoghq.com/ide_plugins/vscode/?tab=cursor) recommended. |
| [Claude Code](https://claude.com/product/claude-code) | Anthropic |  |
| [Claude](https://claude.ai/) | Anthropic | Use [custom connector setup](https://docs.datadoghq.com/bits_ai/mcp_server/setup/?tab=claude#installation). Includes Claude Cowork. |
| [Codex CLI](https://chatgpt.com/codex) | OpenAI |  |
| [Warp](https://www.warp.dev/) | Warp |  |
| [VS Code](https://code.visualstudio.com/) | Microsoft | Datadog [Cursor & VS Code extension](https://docs.datadoghq.com/ide_plugins/vscode/) recommended. |
| [JetBrains IDEs](https://docs.datadoghq.com/ide_plugins/idea/) | JetBrains | [Datadog plugin](https://docs.datadoghq.com/ide_plugins/idea/) recommended. |
| [Kiro](https://kiro.dev/), [Kiro CLI](https://kiro.dev/cli/) | Amazon Web Services |  |
| [Goose](https://github.com/block/goose), [Cline](https://cline.bot/) | Various | See the **Other** tab above. Use local binary authentication for Cline if remote authentication is unreliable. |

> [!info] Info
> The Datadog MCP Server is under significant development, and additional supported clients may become available.

## Required permissions

MCP Server tools require the following [Datadog user role permissions](https://docs.datadoghq.com/account_management/rbac/permissions/#mcp):

| Permission | Required for |
| --- | --- |
| `mcp_read` | Tools that read data from Datadog (for example, querying monitors, searching logs, retrieving dashboards) |
| `mcp_write` | Tools that create or modify resources in Datadog (for example, creating monitors, muting hosts) |

In addition to `mcp_read` or `mcp_write`, users need the standard Datadog permissions for the underlying resource. For example, using an MCP tool that reads monitors requires both `mcp_read` and the [Monitors Read](https://docs.datadoghq.com/account_management/rbac/permissions/#monitors) permission. See [Datadog Role Permissions](https://docs.datadoghq.com/account_management/rbac/permissions/) for the full list of resource-level permissions.

Users with the **Datadog Standard Role** have both MCP Server permissions by default. If your organization uses [custom roles](https://docs.datadoghq.com/account_management/rbac/?tab=datadogapplication#custom-roles), add the permissions manually:

1. Go to [**Organization Settings > Roles**](https://app.datadoghq.com/organization-settings/roles) as an administrator, and click the role you want to update.
2. Click **Edit Role** (pencil icon).
3. Under the permissions list, select the **MCP Read** and **MCP Write** checkboxes.
4. Select any other resource-level permissions you need for the role.
5. Click **Save**.

Organization administrators can manage global MCP access and write capabilities from [Organization Settings](https://app.datadoghq.com/organization-settings/preferences).

## Authentication

The MCP Server uses OAuth 2.0 for [authentication](https://modelcontextprotocol.io/specification/draft/basic/authorization). If you cannot go through the OAuth flow (for example, on a server), you can provide a Datadog [API key and application key](https://docs.datadoghq.com/account_management/api-app-keys/) as `DD_API_KEY` and `DD_APPLICATION_KEY` HTTP headers.

For example, based on your selected [Datadog site](https://docs.datadoghq.com/getting_started/site/#navigate-the-datadog-documentation-by-site) (US1):

```
{
  "mcpServers": {
    "datadog": {
      "type": "http",
      "url": "https://mcp.datadoghq.com/api/unstable/mcp-server/mcp",
      "headers": {
          "DD_API_KEY": "<YOUR_API_KEY>",
          "DD_APPLICATION_KEY": "<YOUR_APPLICATION_KEY>"
      }
    }
  }
}
```

For security, use a scoped API key and application key from a [service account](https://docs.datadoghq.com/account_management/org_settings/service_accounts/) that has only the required permissions.

### Local binary authentication

Local authentication is recommended for Cline and when remote authentication is unreliable or not available. After installation, you typically do not need to update the local binary to benefit from MCP Server updates, as the tools are remote.

##### Set up Datadog MCP Server local binary

1. Install the Datadog MCP Server binary (macOS and Linux):
	```bash
	curl -sSL https://coterm.datadoghq.com/mcp-cli/install.sh | bash
	```
	This installs the binary to `~/.local/bin/datadog_mcp_cli`.
	For Windows, download the [Windows version](https://coterm.datadoghq.com/mcp-cli/datadog_mcp_cli.exe).
2. Run `datadog_mcp_cli login` manually to walk through the OAuth login flow and choose a [Datadog site](https://docs.datadoghq.com/getting_started/site/).
3. Configure your AI client to use the stdio transport with `datadog_mcp_cli` as the command. For example, in macOS (replace `<USERNAME>` with your OS username):
	```json
	{
	  "mcpServers": {
	    "datadog": {
	      "type": "stdio",
	      "command": "/Users/<USERNAME>/.local/bin/datadog_mcp_cli",
	      "args": [],
	      "env": {}
	    }
	  }
	}
	```
	For other operating systems, replace the `command` path with the location of the downloaded binary:
	- Linux: `/home/<USERNAME>/.local/bin/datadog_mcp_cli`
		- Windows: `<USERNAME>\bin\datadog_mcp_cli.exe`
	> [!tip] Tip
	> For Claude Code, you can instead run:
	> ```
	> claude mcp add datadog --scope user -- ~/.local/bin/datadog_mcp_cli
	> ```
4. Fully restart your AI client to apply the configuration and load the MCP Server.

## Test access to the MCP Server

1. Install the [MCP inspector](https://github.com/modelcontextprotocol/inspector), a developer tool for testing and debugging MCP servers.
	```bash
	npx @modelcontextprotocol/inspector
	```
2. In the inspector’s web UI, for **Transport Type**, select **Streamable HTTP**.
3. For **URL**, enter the MCP Server endpoint for your regional Datadog site.
	For example, for US1: `https://mcp.datadoghq.com/api/unstable/mcp-server/mcp`
4. Click **Connect**, then go to **Tools** > **List Tools**.
5. Check if the [available tools](https://docs.datadoghq.com/bits_ai/mcp_server/tools) appear.

## Further reading

Additional helpful documentation, links, and articles:

[Datadog MCP ServerDOCUMENTATION ![](https://docs.dd-static.net/images/icons/list-group-whats-next-arrow-1.png?fit=max&auto=format&w=807) ![more](https://docs.dd-static.net/images/icons/list-group-whats-next-arrow-2.png?fit=max&auto=format&w=807)](https://docs.datadoghq.com/bits_ai/mcp_server)   [Datadog MCP Server ToolsDOCUMENTATION ![](https://docs.dd-static.net/images/icons/list-group-whats-next-arrow-1.png?fit=max&auto=format&w=807) ![more](https://docs.dd-static.net/images/icons/list-group-whats-next-arrow-2.png?fit=max&auto=format&w=807)](https://docs.datadoghq.com/bits_ai/mcp_server/tools)   [Datadog Extension for CursorDOCUMENTATION ![](https://docs.dd-static.net/images/icons/list-group-whats-next-arrow-1.png?fit=max&auto=format&w=807) ![more](https://docs.dd-static.net/images/icons/list-group-whats-next-arrow-2.png?fit=max&auto=format&w=807)](https://docs.datadoghq.com/ide_plugins/vscode/?tab=cursor)  

```
LanguageDatadog Site
```

![datadog bits](https://docs.dd-static.net/images/dd-logo-white.svg)

```yaml
rulesets:
  - %!s(<nil>)     # Rules to enforce .
```

## Can't find something?

Our friendly, knowledgeable solutions engineers are here to help!

Download mobile appProduct

resources

About

Blog

##### Get Started with Datadog

<iframe src="" width="540px" height="805" frameborder="0" title="Sign Up for Datadog"></iframe>

<img src="//bat.bing.com/action/0?ti=4061438&amp;Ver=2" height="0" width="0" style="display:none; visibility: hidden;">

    <iframe title="_hjSafeContext" src="about:blank"></iframe><iframe title="_hjSafeContext" src="about:blank"></iframe>

## Was this page helpful?

 Yes 🎉  No 👎