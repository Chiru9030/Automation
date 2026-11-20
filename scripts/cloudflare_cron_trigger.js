/**
 * Cloudflare Worker: Reliable External Cron Dispatcher & Heartbeat Monitor
 * Free tier: 100,000 requests/day, 100% reliable cron triggers (no GitHub Actions dropped crons).
 *
 * Setup:
 * 1. Create a free Cloudflare Worker at https://workers.cloudflare.com
 * 2. Set Cron Trigger to '0 14 * * *' (Once daily at 14:00 UTC)
 * 3. Add Environment Variables / Secrets in Cloudflare Worker settings:
 *    - GITHUB_PAT: Fine-grained personal access token with 'Actions: Read & Write' permission
 *    - GITHUB_REPO: 'Chiru9030/Automation'
 *    - TELEGRAM_BOT_TOKEN (optional): For heartbeat & failure alerts
 *    - TELEGRAM_CHAT_ID (optional): Your Telegram chat ID
 */

export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(triggerGitHubWorkflow(env));
  },

  async fetch(request, env, ctx) {
    // Manual trigger endpoint for testing: GET https://your-worker.workers.dev/run
    const result = await triggerGitHubWorkflow(env);
    return new Response(JSON.stringify(result, null, 2), {
      headers: { "Content-Type": "application/json" }
    });
  }
};

async function sendTelegramAlert(env, message) {
  if (!env.TELEGRAM_BOT_TOKEN || !env.TELEGRAM_CHAT_ID) return;
  try {
    const tgUrl = `https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`;
    await fetch(tgUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: env.TELEGRAM_CHAT_ID,
        text: message,
        parse_mode: "Markdown"
      })
    });
  } catch (err) {
    console.error("Telegram alert failed:", err);
  }
}

async function triggerGitHubWorkflow(env) {
  const repo = env.GITHUB_REPO || "Chiru9030/Automation";
  const workflowFile = "story_pipeline.yml";
  const url = `https://api.github.com/repos/${repo}/actions/workflows/${workflowFile}/dispatches`;

  const headers = {
    "Authorization": `Bearer ${env.GITHUB_PAT}`,
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "Cloudflare-Worker-Story-Cron"
  };

  const body = {
    ref: "main",
    inputs: {
      sample_mode: false,
      privacy_status: "private" // Uploads as private for safe human review before public
    }
  };

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: headers,
      body: JSON.stringify(body)
    });

    if (response.status === 204) {
      console.log("✅ Successfully dispatched GitHub Actions workflow!");
      await sendTelegramAlert(
        env,
        `🟢 *[Pipeline Heartbeat]* Daily YouTube Shorts Pipeline triggered successfully via Cloudflare Worker!\n⏰ *Time:* ${new Date().toISOString()}`
      );
      return { success: true, message: "Workflow dispatched successfully." };
    } else {
      const errText = await response.text();
      console.error(`Failed to dispatch workflow: ${response.status} - ${errText}`);
      await sendTelegramAlert(
        env,
        `🚨 *[Pipeline Trigger Alert]* Cloudflare Worker failed to start GitHub Actions!\n*Status:* ${response.status}\n*Details:* \`${errText.slice(0, 150)}\``
      );
      return { success: false, status: response.status, error: errText };
    }
  } catch (error) {
    console.error("Fetch error:", error);
    await sendTelegramAlert(
      env,
      `🚨 *[Pipeline Trigger Fatal]* Cloudflare Worker encountered network error: \`${error.message}\``
    );
    return { success: false, error: error.message };
  }
}
