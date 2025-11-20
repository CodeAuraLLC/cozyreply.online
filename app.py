import os
from flask import Flask, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from gemini_client import generate_text
from storage import (
    get_user,
    create_user,
    get_listing_details,
    save_listing_details,
    add_conversation,
    get_recent_conversations,
)

app = Flask(__name__)
app.secret_key = "replace-this-with-a-random-secret-string"  # change later for production

# ---------- HTML TEMPLATES (INLINE) ----------

LANDING_PAGE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>CozyReply.ai – AI co-host for guest messaging</title>
  </head>
  <body style="margin:0; padding:0; background:#f5f5f5; font-family:system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
    <div style="max-width:960px;margin:0 auto;padding:24px;min-height:100vh;">

      <!-- Navbar -->
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:24px;">
        <div style="display:flex;align-items:center;gap:8px;">
          <div style="width:30px;height:30px;border-radius:999px;background:linear-gradient(135deg,#FF5A5F,#FF7A85);display:flex;align-items:center;justify-content:center;color:white;font-weight:700;">
            C
          </div>
          <span style="font-size:13px;letter-spacing:0.12em;text-transform:uppercase;color:#777;">
            CozyReply
          </span>
        </div>
        <div style="font-size:12px;">
          <a href="{login_url}" style="margin-right:12px;color:#555;text-decoration:none;">Log in</a>
          <a href="{register_url}" style="padding:7px 14px;border-radius:999px;border:1px solid #FF5A5F;color:#FF5A5F;text-decoration:none;font-weight:600;">
            Get started free
          </a>
        </div>
      </div>

      <!-- Hero -->
      <div style="display:flex;flex-wrap:wrap;gap:18px;margin-bottom:24px;align-items:center;">
        <div style="flex:2 1 260px; position:relative;">
          <h1 style="margin:4px 0 8px;font-size:32px;font-weight:700;color:#222;">
            Your AI co-host for guest messages.
          </h1>
          <p style="margin:0 0 10px;font-size:14px;color:#555;">
            CozyReply.ai drafts warm, rule-aware replies to guest questions so you can focus on hosting – not your inbox.
          </p>
          <ul style="margin:10px 0 12px;padding-left:18px;font-size:13px;color:#555;line-height:1.5;">
            <li>✅ Draft replies for check-ins, checkouts, and rule reminders</li>
            <li>✅ Save your house rules & listing details once</li>
            <li>✅ Keep your tone consistent across every stay</li>
          </ul>
          <a href="{register_url}" style="display:inline-block;margin-top:4px;padding:10px 20px;border-radius:999px;background:linear-gradient(135deg,#FF5A5F,#FF7A85);color:white;font-size:13px;font-weight:600;text-decoration:none;box-shadow:0 10px 22px rgba(255,90,95,0.35);">
            Start free – no credit card
          </a>
          <p style="margin:8px 0 0;font-size:11px;color:#999;">
            Not affiliated with Airbnb. You stay in control of what gets sent.
          </p>
        </div>

        <!-- Hero card / “screenshot” -->
        <div style="flex:1 1 230px;">
          <div style="border-radius:20px;background:linear-gradient(145deg,#FF5A5F,#FFB199);padding:14px;color:white;box-shadow:0 14px 32px rgba(0,0,0,0.18);">
            <div style="display:flex;align-items:flex-start;gap:10px;margin-bottom:8px;">
              <div style="width:42px;height:42px;border-radius:999px;background:rgba(255,255,255,0.16);display:flex;align-items:center;justify-content:center;font-size:24px;">
                🛫
              </div>
              <div>
                <div style="font-size:14px;font-weight:600;">Turn “Can we…?” into “Thanks so much!”</div>
                <div style="font-size:11px;opacity:0.9;margin-top:3px;">
                  Paste a guest message, and CozyReply drafts a friendly, rule-aligned response in seconds.
                </div>
              </div>
            </div>
            <div style="margin-top:8px;border-radius:12px;background:rgba(17,24,39,0.85);padding:8px 10px;font-size:11px;line-height:1.5;">
              <div style="opacity:0.8;margin-bottom:4px;">Guest:</div>
              <div style="opacity:1;">“Hi! Can we check in early and invite a few friends over?”</div>
              <div style="height:1px;background:rgba(249,250,251,0.16);margin:7px 0;"></div>
              <div style="opacity:0.8;margin-bottom:2px;">CozyReply draft:</div>
              <div style="opacity:1;">
                “Thanks so much for reaching out! Check-in is normally after 3pm, but I can let you know on the day if the space is ready earlier. Just a quick note that the home is for registered guests only and we have quiet hours after 10pm to respect the neighbors…”
              </div>
            </div>
            <div style="margin-top:10px;font-size:10px;opacity:0.85;">
              Works alongside your existing Airbnb or short-term rental account. CozyReply never sends messages for you – it just drafts them.
            </div>
          </div>
        </div>
      </div>

      <!-- Feature cards -->
      <div style="display:flex;flex-wrap:wrap;gap:12px;margin-bottom:18px;">
        <div style="flex:1 1 200px;background:#fff;border-radius:14px;padding:12px;border:1px solid #ebebeb;font-size:12px;">
          <div style="font-weight:600;margin-bottom:4px;">🌙 Late-night messages</div>
          <div style="color:#666;">Handle “can we check in at 1am?” and last-minute questions without retyping your rules.</div>
        </div>
        <div style="flex:1 1 200px;background:#fff;border-radius:14px;padding:12px;border:1px solid #ebebeb;font-size:12px;">
          <div style="font-weight:600;margin-bottom:4px;">📋 House rules, remembered</div>
          <div style="color:#666;">Save your quiet hours, parking info, and no-party policy once. CozyReply references them in every reply.</div>
        </div>
        <div style="flex:1 1 200px;background:#fff;border-radius:14px;padding:12px;border:1px solid #ebebeb;font-size:12px;">
          <div style="font-weight:600;margin-bottom:4px;">🧳 Check-in & checkout</div>
          <div style="color:#666;">Use templates to generate clear check-in and checkout instructions tailored to each guest.</div>
        </div>
      </div>

      <!-- Mini pricing teaser -->
      <div style="background:#fff;border-radius:16px;padding:14px 16px;border:1px solid #ebebeb;box-shadow:0 8px 20px rgba(0,0,0,0.04);font-size:12px;margin-bottom:12px;">
        <div style="display:flex;flex-wrap:wrap;justify-content:space-between;gap:8px;align-items:center;">
          <div>
            <div style="font-weight:600;margin-bottom:2px;">Right now: early access</div>
            <div style="color:#666;">Try CozyReply.ai while it’s in beta. Free to use while we collect feedback from real hosts.</div>
          </div>
          <div>
            <a href="{register_url}" style="padding:8px 16px;border-radius:999px;background:linear-gradient(135deg,#FF5A5F,#FF7A85);color:white;font-size:12px;font-weight:600;text-decoration:none;display:inline-block;">
              Create a free account
            </a>
          </div>
        </div>
      </div>

      <footer style="margin-top:12px;text-align:center;font-size:11px;color:#aaa;">
        CozyReply.ai is an independent tool for short-term rental hosts. Not affiliated with or endorsed by Airbnb.
      </footer>
    </div>
  </body>
</html>
"""

LOGIN_PAGE = """
<!doctype html>
<html lang="en">
  <head><meta charset="utf-8"><title>Login · CozyReply</title></head>
  <body style="margin:0; padding:0; background:#f5f5f5; font-family:system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
    <div style="max-width:420px; margin:40px auto; padding:24px;">
      <div style="text-align:center; margin-bottom:18px;">
        <div style="display:inline-flex; align-items:center; gap:8px;">
          <div style="width:32px;height:32px;border-radius:999px;background:linear-gradient(135deg,#FF5A5F,#FF7A85);display:flex;align-items:center;justify-content:center;color:white;font-weight:700;">C</div>
          <span style="font-size:13px;letter-spacing:0.12em;text-transform:uppercase;color:#777;">CozyReply</span>
        </div>
        <h1 style="margin:10px 0 4px;font-size:22px;font-weight:700;color:#222;">Welcome back</h1>
        <p style="margin:0;font-size:13px;color:#717171;">Sign in to your host reply assistant.</p>
      </div>
      <div style="background:#fff;border-radius:18px;padding:20px 18px;border:1px solid #ebebeb;box-shadow:0 10px 24px rgba(0,0,0,0.06);">
        <form method="POST" style="display:flex;flex-direction:column;gap:10px;">
          <label style="font-size:13px;font-weight:600;color:#484848;">Email</label>
          <input name="email" type="email" required
            style="border-radius:999px;border:1px solid #dcdcdc;padding:8px 12px;font-size:13px;box-sizing:border-box;width:100%;" />

          <label style="font-size:13px;font-weight:600;color:#484848;">Password</label>
          <input name="password" type="password" required
            style="border-radius:999px;border:1px solid #dcdcdc;padding:8px 12px;font-size:13px;box-sizing:border-box;width:100%;" />

          <button type="submit"
            style="margin-top:6px;border:none;border-radius:999px;padding:9px 16px;background:linear-gradient(135deg,#FF5A5F,#FF7A85);color:#fff;font-weight:600;font-size:13px;cursor:pointer;box-shadow:0 8px 16px rgba(255,90,95,0.35);">
            Log in
          </button>
        </form>
        <p style="margin:10px 0 0;font-size:12px;color:#999;text-align:center;">
          Don't have an account?
          <a href="{register_url}" style="color:#FF5A5F;text-decoration:none;font-weight:600;">Sign up</a>
        </p>
        {error_block}
      </div>
    </div>
  </body>
</html>
"""

REGISTER_PAGE = """
<!doctype html>
<html lang="en">
  <head><meta charset="utf-8"><title>Sign up · CozyReply</title></head>
  <body style="margin:0; padding:0; background:#f5f5f5; font-family:system-ui, -apple-system, BlinkMacSystemFont,'Segoe UI',sans-serif;">
    <div style="max-width:420px; margin:40px auto; padding:24px;">
      <div style="text-align:center; margin-bottom:18px;">
        <div style="display:inline-flex; align-items:center; gap:8px;">
          <div style="width:32px;height:32px;border-radius:999px;background:linear-gradient(135deg,#FF5A5F,#FF7A85);display:flex;align-items:center;justify-content:center;color:white;font-weight:700;">C</div>
          <span style="font-size:13px;letter-spacing:0.12em;text-transform:uppercase;color:#777;">CozyReply</span>
        </div>
        <h1 style="margin:10px 0 4px;font-size:22px;font-weight:700;color:#222;">Create your host account</h1>
        <p style="margin:0;font-size:13px;color:#717171;">Save your listing & reply history per account.</p>
      </div>
      <div style="background:#fff;border-radius:18px;padding:20px 18px;border:1px solid #ebebeb;box-shadow:0 10px 24pxrgba(0,0,0,0.06);">
        <form method="POST" style="display:flex;flex-direction:column;gap:10px;">
          <label style="font-size:13px;font-weight:600;color:#484848;">Email</label>
          <input name="email" type="email" required
            style="border-radius:999px;border:1px solid #dcdcdc;padding:8px 12px;font-size:13px;box-sizing:border-box;width:100%;" />

          <label style="font-size:13px;font-weight:600;color:#484848;">Password</label>
          <input name="password" type="password" required
            style="border-radius:999px;border:1px solid #dcdcdc;padding:8px 12px;font-size:13px;box-sizing:border-box;width:100%;" />

          <label style="font-size:13px;font-weight:600;color:#484848;">Confirm password</label>
          <input name="password2" type="password" required
            style="border-radius:999px;border:1px solid #dcdcdc;padding:8px 12px;font-size:13px;box-sizing:border-box;width:100%;" />

          <button type="submit"
            style="margin-top:6px;border:none;border-radius:999px;padding:9px 16px;background:linear-gradient(135deg,#FF5A5F,#FF7A85);color:#fff;font-weight:600;font-size:13px;cursor:pointer;box-shadow:0 8px 16px rgba(255,90,95,0.35);">
            Sign up
          </button>
        </form>
        <p style="margin:10px 0 0;font-size:12px;color:#999;text-align:center;">
          Already have an account?
          <a href="{login_url}" style="color:#FF5A5F;text-decoration:none;font-weight:600;">Log in</a>
        </p>
        {error_block}
      </div>
    </div>
  </body>
</html>
"""

MAIN_PAGE = """
<!doctype html>
<html lang="en">
  <head><meta charset="utf-8"><title>CozyReply · Host Automator</title></head>
  <body style="margin:0; padding:0; background-color:#f5f5f5; font-family:system-ui, -apple-system, BlinkMacSystemFont,'Segoe UI',sans-serif;">
    <div style="max-width:960px; margin:0 auto; padding:24px; min-height:100vh;">

      <!-- Top nav -->
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
        <div style="display:flex; align-items:center; gap:8px;">
          <div style="width:30px;height:30px;border-radius:999px;background:linear-gradient(135deg,#FF5A5F,#FF7A85);display:flex;align-items:center;justify-content:center;color:white;font-weight:700;">C</div>
          <span style="font-size:13px;letter-spacing:0.12em;text-transform:uppercase;color:#777;">CozyReply</span>
        </div>
        <div style="font-size:12px;color:#777;">
          <span style="margin-right:10px;">Logged in as <strong style="color:#444;">{user_email}</strong></span>
          <a href="{logout_url}" style="color:#FF5A5F;text-decoration:none;font-weight:600;">Log out</a>
        </div>
      </div>

      <!-- Hero row -->
      <div style="display:flex; flex-wrap:wrap; gap:16px; margin-bottom:18px;">
        <div style="flex:2 1 260px;">
          <h1 style="margin:4px 0 4px; font-size:26px; font-weight:700; color:#222222;">
            Draft Airbnb-style replies in seconds.
          </h1>
          <p style="margin:0 0 10px; font-size:13px; color:#717171;">
            CozyReply turns guest questions into clear, friendly responses that respect your house rules and vibe.
          </p>
          <div style="display:flex; gap:8px; font-size:11px; color:#9b9b9b; flex-wrap:wrap;">
            <span style="padding:4px 8px;border-radius:999px;border:1px solid #ebebeb;background:#fff;">✈️ Travel stays</span>
            <span style="padding:4px 8px;border-radius:999px;border:1px solid #ebebeb;background:#fff;">🏡 Home shares</span>
            <span style="padding:4px 8px;border-radius:999px;border:1px solid #ebebeb;background:#fff;">⏱️ Faster hosting</span>
          </div>
        </div>
        <div style="flex:1 1 200px;">
          <div style="
            border-radius:20px;
            background:linear-gradient(145deg,#FF5A5F,#FFB199);
            padding:14px;
            color:white;
            box-shadow:0 14px 32px rgba(0,0,0,0.18);
            height:100%;
            display:flex;
            flex-direction:column;
            justify-content:space-between;
          ">
            <div style="display:flex; align-items:flex-start; gap:10px;">
              <div style="
                width:40px;height:40px;border-radius:999px;
                background:rgba(255,255,255,0.16);
                display:flex;align-items:center;justify-content:center;
                font-size:22px;">
                🛫
              </div>
              <div>
                <div style="font-size:13px;font-weight:600;">Inbox autopilot (assist)</div>
                <div style="font-size:11px;opacity:0.9;margin-top:2px;">
                  Draft replies for check-ins, checkouts, and rule reminders without losing your personal voice.
                </div>
              </div>
            </div>
            <div style="font-size:10px;opacity:0.8;margin-top:10px;">
              CozyReply never sends messages for you – it just drafts them. You stay in control.
            </div>
          </div>
        </div>
      </div>

      <!-- Main card -->
      <div style="
        background-color:#ffffff;
        border-radius:18px;
        padding:24px 24px 20px;
        box-shadow:0 12px 30px rgba(0,0,0,0.08);
        border:1px solid #ebebeb;
        margin-bottom:18px;
      ">
        <form method="POST" style="display:flex; flex-direction:column; gap:16px;">

          <!-- Listing details -->
          <div>
            <label style="display:block; font-size:13px; font-weight:600; color:#484848; margin-bottom:6px;">
              Listing details &amp; house rules
            </label>
            <p style="margin:0 0 6px; font-size:11px; color:#9b9b9b;">
              Saved automatically for your account. Description, check-in info, quiet hours, parking, “no parties”, etc.
            </p>
            <textarea
              name="listing_details"
              rows="5"
              style="
                width:100%;
                border-radius:12px;
                border:1px solid #dcdcdc;
                padding:10px 12px;
                font-size:13px;
                resize:vertical;
                box-sizing:border-box;
              "
              placeholder="Cozy 2 bed / 1 bath in downtown. Check-in after 3pm, quiet hours after 10pm, no smoking, no parties, street parking only, keypad on front door..."
            >{listing_details}</textarea>
          </div>

          <!-- Guest message -->
          <div>
            <label style="display:block; font-size:13px; font-weight:600; color:#484848; margin-bottom:6px;">
              Guest message
            </label>
            <textarea
              name="guest_message"
              rows="4"
              style="
                width:100%;
                border-radius:12px;
                border:1px solid #dcdcdc;
                padding:10px 12px;
                font-size:13px;
                resize:vertical;
                box-sizing:border-box;
              "
              placeholder="Paste the guest’s message here. Example: “Hi! Can we check in early and have a few friends over for drinks?”"
            ></textarea>
          </div>

          <!-- Tone + template + extra -->
          <div style="display:flex; flex-wrap:wrap; gap:16px;">

            <div style="flex:1 1 160px; min-width:160px;">
              <label style="display:block; font-size:13px; font-weight:600; color:#484848; margin-bottom:6px;">
                Tone
              </label>
              <select
                name="tone"
                style="
                  width:100%;
                  border-radius:999px;
                  border:1px solid #dcdcdc;
                  padding:8px 12px;
                  font-size:13px;
                  background-color:#ffffff;
                  box-sizing:border-box;
                "
              >
                <option value="friendly">Friendly / Casual</option>
                <option value="professional">Professional / Polite</option>
                <option value="strict">Firm but Polite (rules-focused)</option>
              </select>
            </div>

            <div style="flex:1 1 180px; min-width:180px;">
              <label style="display:block; font-size:13px; font-weight:600; color:#484848; margin-bottom:6px;">
                Reply template
              </label>
              <select
                name="template_type"
                style="
                  width:100%;
                  border-radius:999px;
                  border:1px solid #dcdcdc;
                  padding:8px 12px;
                  font-size:13px;
                  background-color:#ffffff;
                  box-sizing:border-box;
                "
              >
                <option value="normal">Normal reply</option>
                <option value="checkin">Check-in instructions</option>
                <option value="checkout">Checkout reminder</option>
                <option value="rules_reminder">House rules reminder</option>
              </select>
            </div>

            <div style="flex:2 1 220px; min-width:220px;">
              <label style="display:block; font-size:13px; font-weight:600; color:#484848; margin-bottom:6px;">
                Extra instructions (optional)
              </label>
              <textarea
                name="extra"
                rows="3"
                style="
                  width:100%;
                  border-radius:12px;
                  border:1px solid #dcdcdc;
                  padding:10px 12px;
                  font-size:13px;
                  resize:vertical;
                  box-sizing:border-box;
                "
                placeholder="Example: Emphasize quiet hours after 10pm. Offer early check-in only if cleaning is finished. Mention street parking rules."
              ></textarea>
            </div>
          </div>

          <!-- Button + hint -->
          <div style="display:flex; align-items:center; gap:12px; margin-top:4px;">
            <button
              type="submit"
              style="
                border:none;
                border-radius:999px;
                padding:10px 20px;
                background:linear-gradient(135deg,#FF5A5F,#FF7A85);
                color:white;
                font-weight:600;
                font-size:13px;
                cursor:pointer;
                box-shadow:0 8px 16px rgba(255,90,95,0.35);
              "
            >
              Generate reply
            </button>
            <span style="font-size:11px; color:#9b9b9b;">
              Your listing is saved to this account whenever you generate a reply.
            </span>
          </div>
        </form>

        <!-- Reply box -->
        <div style="margin-top:22px;">
          <h2 style="margin:0 0 6px; font-size:14px; font-weight:600; color:#484848;">
            Suggested reply
          </h2>
          <div style="
            border-radius:14px;
            background-color:#111827;
            color:#e5e7eb;
            padding:12px 14px;
            font-size:13px;
            line-height:1.5;
            white-space:pre-wrap;
            min-height:80px;
          ">
{reply}
          </div>
          <p style="margin:6px 0 0; font-size:11px; color:#9b9b9b;">
            Tip: select this text, copy, and paste it directly into your Airbnb inbox.
          </p>
        </div>
      </div>

      <!-- Recent replies panel -->
      <div style="
        background-color:#ffffff;
        border-radius:16px;
        padding:16px 18px;
        box-shadow:0 8px 20px rgba(0,0,0,0.06);
        border:1px solid #ebebeb;
      ">
        <h2 style="margin:0 0 8px; font-size:14px; font-weight:600; color:#484848;">
          Recent replies (last 3)
        </h2>
        <div style="font-size:12px; color:#555;">
{recent_html}
        </div>
      </div>

      <!-- Footer -->
      <footer style="margin-top:16px; font-size:11px; color:#b0b0b0; text-align:center;">
        CozyReply.ai is not affiliated with Airbnb. It helps hosts draft replies faster while they stay in control.
      </footer>
    </div>
  </body>
</html>
"""

# ---------- HELPERS ----------

def build_prompt(listing_details, guest_message, tone, extra, template_type):
    tone_instruction = {
        "friendly": "Use a warm, friendly, casual tone.",
        "professional": "Use a polite, professional, clear tone.",
        "strict": "Be firm but respectful. Enforce rules clearly.",
    }.get(tone, "Use a neutral, helpful tone.")

    if template_type == "checkin":
        type_instruction = (
            "Write a friendly check-in instructions message. Include arrival time window, "
            "how to access the property (keypad / lockbox), parking instructions, and any "
            "important first-night details. Reference their question if they asked something."
        )
    elif template_type == "checkout":
        type_instruction = (
            "Write a polite checkout reminder message. Include checkout time, any simple "
            "checkout tasks (trash, dishes, keys), and thank them for staying."
        )
    elif template_type == "rules_reminder":
        type_instruction = (
            "Write a polite reminder of the key house rules relevant to their question. "
            "Be clear but not harsh. Emphasize respect for neighbors, quiet hours, and any "
            "important restrictions (no parties, no smoking, etc.)."
        )
    else:
        type_instruction = "Write a normal reply to the guest's message, answering questions and clarifying anything needed."

    prompt = f"""
You are an AI assistant for short-term rental hosts called CozyReply.

Your job:
- Read the listing details and house rules.
- Read the guest's message.
- {type_instruction}
- {tone_instruction}
- Be concise and easy to read.
- Do NOT invent facts that are not in the listing.
- If the guest asks for something against the rules, decline politely and explain why.
- Do not include emojis unless it's minimal and natural.
- Do not include the host's real name unless one is provided.

LISTING DETAILS & HOUSE RULES:
\"\"\"{listing_details}\"\"\"

GUEST MESSAGE:
\"\"\"{guest_message}\"\"\"

EXTRA NOTES FROM HOST:
\"\"\"{extra}\"\"\"

Now write the final reply message to send to the guest on Airbnb or a similar platform.
    """
    return prompt

def render_recent_html(convos):
    if not convos:
        return "<p style='margin:4px 0 0; color:#9b9b9b;'>No replies yet. Generate one and it will appear here.</p>"
    blocks = []
    for c in convos:
        guest_preview = c["guest_message"]
        if len(guest_preview) > 120:
            guest_preview = guest_preview[:120] + "…"
        reply_preview = c["reply"]
        if len(reply_preview) > 160:
            reply_preview = reply_preview[:160] + "…"
        block = f"""
<div style="border-radius:10px; border:1px solid #f0f0f0; padding:8px 10px; margin-bottom:6px; background-color:#fafafa;">
  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
    <span style="font-weight:600; color:#444;">
      {c['template_type'].replace('_', ' ').title()} · {c['tone'].title()}
    </span>
    <span style="font-size:10px; color:#999;">
      {c['timestamp']}
    </span>
  </div>
  <div style="color:#777;">
    <strong>Guest:</strong> {guest_preview}
  </div>
    <div style="margin-top:3px; color:#444;">
    <strong>Reply:</strong> {reply_preview}
  </div>
</div>
"""
        blocks.append(block)
    return "".join(blocks)

def current_user_email():
    return session.get("user_email")

def require_login():
    return "user_email" in session

# ---------- ROUTES ----------

@app.route("/")
def home():
    # If already logged in, go straight to app dashboard
    if require_login():
        return redirect(url_for("index"))
    return LANDING_PAGE.format(
        login_url=url_for("login"),
        register_url=url_for("register"),
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    error_block = ""
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        user = get_user(email)
        if not user or not check_password_hash(user["password_hash"], password):
            error_block = "<p style='margin-top:10px;font-size:12px;color:#d93025;'>Invalid email or password.</p>"
        else:
            session["user_email"] = email
            return redirect(url_for("index"))

    return LOGIN_PAGE.format(
        register_url=url_for("register"),
        error_block=error_block,
    )

@app.route("/register", methods=["GET", "POST"])
def register():
    error_block = ""
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        pw1 = request.form.get("password") or ""
        pw2 = request.form.get("password2") or ""

        if not email or not pw1 or not pw2:
            error_block = "<p style='margin-top:10px;font-size:12px;color:#d93025;'>Please fill out all fields.</p>"
        elif pw1 != pw2:
            error_block = "<p style='margin-top:10px;font-size:12px;color:#d93025;'>Passwords do not match.</p>"
        elif get_user(email):
            error_block = "<p style='margin-top:10px;font-size:12px;color:#d93025;'>An account with that email already exists.</p>"
        else:
            password_hash = generate_password_hash(pw1)
            create_user(email, password_hash)
            session["user_email"] = email
            return redirect(url_for("index"))

    return REGISTER_PAGE.format(
        login_url=url_for("login"),
        error_block=error_block,
    )

@app.route("/logout")
def logout():
    session.pop("user_email", None)
    return redirect(url_for("home"))

@app.route("/app", methods=["GET", "POST"])
def index():
    if not require_login():
        return redirect(url_for("login"))
    email = current_user_email()

    listing_details = get_listing_details(email)
    recent_convos = get_recent_conversations(email, limit=3)
    recent_html = render_recent_html(recent_convos)
    reply = ""

    if request.method == "POST":
        listing_details = request.form.get("listing_details", "")
        guest_message = request.form.get("guest_message", "")
        tone = request.form.get("tone", "friendly")
        extra = request.form.get("extra", "")
        template_type = request.form.get("template_type", "normal")

        save_listing_details(email, listing_details)

        if listing_details.strip() and guest_message.strip():
            prompt = build_prompt(listing_details, guest_message, tone, extra, template_type)
            try:
                reply = generate_text(prompt)
                add_conversation(email, guest_message, reply, tone, template_type)
                recent_convos = get_recent_conversations(email, limit=3)
                recent_html = render_recent_html(recent_convos)
            except Exception as e:
                reply = f"[Error talking to Gemini: {e}]"
        else:
            reply = "Please fill in both listing details and the guest message."

    return MAIN_PAGE.format(
        user_email=email,
        listing_details=listing_details,
        reply=reply,
        recent_html=recent_html,
        logout_url=url_for("logout"),
    )

if __name__ == "__main__":
    # use 5050 since 5000 was busy on your Mac
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=True)