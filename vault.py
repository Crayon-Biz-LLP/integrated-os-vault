import streamlit as st
from supabase import create_client
import os

# 1. SECURITY CHECK (Simple Password Gate)
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    
    if not st.session_state["password_correct"]:
        pw = st.text_input("Enter Vault Secret", type="password")
        # You'll need to add VAULT_PASSWORD to your Vercel/Streamlit secrets
        if pw == os.getenv("VAULT_PASSWORD", "danny123"): 
            st.session_state["password_correct"] = True
            st.rerun()
        return False
    return True

if not check_password():
    st.stop()

# 2. INITIALIZE SUPABASE (Using Service Role to bypass RLS)
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") # Use the God Key here
supabase = create_client(url, key)

st.set_page_config(page_title="Integrated OS | Command Center", layout="wide")
st.title("🕹️ Integrated OS: Command Center")

# 3. TABS FOR DEEP WORK
tabs = st.tabs(["🚀 MISSIONS", "📋 BATTLEFIELD (TASKS)", "📚 RESOURCE VAULT"])

# --- TAB 1: MISSIONS ---
with tabs[0]:
    st.header("Active Strategic Missions")
    
    # Fetch Missions with their descriptions
    missions_res = supabase.table('missions').select('*').order('created_at', desc=True).execute()
    
    if missions_res.data:
        for m in missions_res.data:
            with st.expander(f"🎯 {m['title']}", expanded=False):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Status:** {m['status'].upper()}")
                    # 🧠 The Logic: Displaying the AI's reasoning for creating this mission
                    if m.get('description'):
                        st.info(f"**Strategic Intent:** {m['description']}")
                    else:
                        st.write("_No strategic description provided._")
                
                with col2:
                    st.caption(f"Created: {m['created_at'][:10]}")

                st.divider()
                
                # 🔗 Fetch & List Resources belonging to THIS mission
                res_items = supabase.table('resources')\
                    .select('title, url, summary, strategic_note')\
                    .eq('mission_id', m['id'])\
                    .execute()

                if res_items.data:
                    st.write("### 🔖 Mission Components")
                    for r in res_items.data:
                        st.markdown(f"**[{r['title']}]({r['url']})**")
                        if r['summary']:
                            st.write(f"_{r['summary']}_")
                        # 💡 The "Why": AI logic for why this link belongs here
                        if r['strategic_note']:
                            st.caption(f"💡 {r['strategic_note']}")
                        st.write("")
                else:
                    st.write("No resources linked to this mission yet.")
    else:
        st.info("No active missions found. Declare one in Telegram or let the AI detect a pattern.")

# --- TAB 2: TASKS ---
with tabs[1]:
    st.header("The Battlefield")
    tasks = supabase.table('tasks').select('*').order('priority', desc=True).execute()
    if tasks.data:
        # 🟡 FIX: Updated 'use_container_width' to the 2026 'width=stretch' syntax
        st.dataframe(tasks.data, width="stretch", hide_index=True)
    else:
        st.success("Battlefield clear. No pending tasks.")

# --- TAB 3: RESOURCES ---
with tabs[2]:
    st.header("Strategic Research & Sparks")
    search = st.text_input("🔍 Search Library")
    res = supabase.table('resources').select('*, missions(title)').order('created_at', desc=True).execute()
    
    if res.data:
        for item in res.data:
            if not search or search.lower() in item['title'].lower():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"### [{item['title']}]({item['url']})")
                    st.write(item['summary'] or "No summary available.")
                    if item.get('strategic_note'):
                        st.info(f"💡 {item['strategic_note']}")
                with col2:
                    # 🛡️ Safety Check: If 'missions' is None, use an empty dict {}
                    mission_data = item.get('missions') or {}
                    mission_title = mission_data.get('title', 'General')
                    st.write(f"📂 {mission_title}")
                st.divider()