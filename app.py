
import streamlit as st

import database as db
import student
import admin


st.set_page_config(
    page_title="Smart Campus Booking System",
    page_icon="🏫",
    layout="wide"
)

db.init_db()

# Demo credentials. Change before real deployment.
ADMIN_PASSWORD = "admin123"

if "panel" not in st.session_state:
    st.session_state["panel"] = "Home"

if "admin_logged_in" not in st.session_state:
    st.session_state["admin_logged_in"] = False


def go_home():
    st.session_state["panel"] = "Home"


st.sidebar.title("🏫 Smart Campus")
st.sidebar.caption("Resource & Room Booking System")

if st.session_state["panel"] != "Home":
    if st.sidebar.button("← Back to Home", use_container_width=True):
        go_home()
        st.rerun()

    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state["admin_logged_in"] = False
        st.session_state["panel"] = "Home"
        st.rerun()

if st.session_state["panel"] == "Home":
    st.markdown(
        "<h1 style='text-align:center;'>Smart Campus</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='text-align:center;'>"
        "Resource & Room Booking System"
        "</p>",
        unsafe_allow_html=True
    )

    st.divider()

    st.subheader("Welcome to Campus Resource Booking")
    st.write(
        "Book engineering labs, rooms, equipment and auditoriums "
        "through one simple application."
    )

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("### 🎓 Student Panel")
        st.write(
            "Explore resources, submit booking requests, "
            "check approvals and cancel bookings."
        )

        if st.button(
            "Open Student Panel",
            use_container_width=True,
            type="primary"
        ):
            st.session_state["panel"] = "Student"
            st.rerun()

    with col2:
        st.markdown("### 🛡️ Admin Panel")
        st.write(
            "Review requests, approve or reject bookings, "
            "and manage reservation history."
        )

        if st.button(
            "Open Admin Panel",
            use_container_width=True
        ):
            st.session_state["panel"] = "Admin"
            st.rerun()

    st.divider()

    # st.markdown("### What can you book?")
    # c1, c2, c3, c4 = st.columns(4)

    # c1.markdown("#### 🖥️ Equipment")
    # c1.caption("GPU servers, Arduino kits, projectors")

    # c2.markdown("#### 🚪 Rooms")
    # c2.caption("Discussion and project rooms")

    # c3.markdown("#### 🧪 Labs")
    # c3.caption("Computer, AI, physics, chemistry and engineering labs")

    # c4.markdown("#### 🏛️ Auditoriums")
    # c4.caption("Seminar halls and main auditorium")

elif st.session_state["panel"] == "Student":
    student.render_student_panel()

elif st.session_state["panel"] == "Admin":
    if not st.session_state["admin_logged_in"]:
        st.title("🛡️ Admin Login")
        st.write("Only authorized administrators can access this panel.")

        with st.form("admin_login_form"):
            password = st.text_input(
                "Admin Password",
                type="password"
            )

            login = st.form_submit_button(
                "Login",
                use_container_width=True
            )

            if login:
                if password == ADMIN_PASSWORD:
                    st.session_state["admin_logged_in"] = True
                    st.success("Login successful.")
                    st.rerun()
                else:
                    st.error("Incorrect password. Please try again.")

        st.caption(
            "Demo password: admin123 — change it in app.py."
        )

    else:
        admin.render_admin_panel()
