
import streamlit as st
import pandas as pd
import database as db


CATEGORIES = [
    "Lab",
    "Room",
    "Auditorium",
    "Equipment",
    "Sports Equipment",
    "Other"
]


def render_resource_management():
    st.subheader("Manage Campus Resources")

    add_tab, view_tab, edit_tab, delete_tab = st.tabs([
        "➕ Add Resource",
        "📋 View Resources",
        "✏️ Edit Resource",
        "🗑️ Delete Resource"
    ])

    # ADD RESOURCE
    with add_tab:
        with st.form("add_resource_form"):
            name = st.text_input("Resource Name")

            category = st.selectbox(
                "Category",
                CATEGORIES,
                key="add_resource_category"
            )

            department = st.text_input(
                "Department",
                placeholder="e.g. AI & Data Science"
            )

            capacity = st.number_input(
                "Capacity / Quantity",
                min_value=1,
                max_value=10000,
                value=1
            )

            specifications = st.text_area(
                "Specifications",
                placeholder="Equipment, facilities, or details"
            )

            guidelines = st.text_area(
                "Usage Guidelines",
                placeholder="Rules students must follow"
            )

            submitted = st.form_submit_button(
                "Add Resource",
                use_container_width=True
            )

            if submitted:
                if not name.strip() or not department.strip():
                    st.error("Resource name and department are required.")
                else:
                    success, message = db.add_resource(
                        name,
                        category,
                        department,
                        int(capacity),
                        specifications,
                        guidelines
                    )

                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

    # VIEW RESOURCES
    with view_tab:
        resources = db.get_resources()

        if resources:
            search = st.text_input(
                "Search resources",
                key="resource_search"
            )

            rows = []

            for r in resources:
                if search.strip().lower() in (
                    r["name"] + " " +
                    r["category"] + " " +
                    r["department"]
                ).lower():
                    rows.append({
                        "ID": r["id"],
                        "Name": r["name"],
                        "Category": r["category"],
                        "Department": r["department"],
                        "Capacity / Quantity": r["capacity"],
                        "Specifications": r["specifications"],
                        "Guidelines": r["guidelines"]
                    })

            if rows:
                st.dataframe(
                    pd.DataFrame(rows),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No matching resources found.")
        else:
            st.info("No resources found.")

    # EDIT RESOURCE
    with edit_tab:
        resources = db.get_resources()

        if resources:
            resource_map = {
                f'{r["name"]} (ID: {r["id"]})': r
                for r in resources
            }

            selected_label = st.selectbox(
                "Choose resource to edit",
                list(resource_map.keys()),
                key="edit_resource_choice"
            )

            selected = resource_map[selected_label]

            category_index = (
                CATEGORIES.index(selected["category"])
                if selected["category"] in CATEGORIES
                else 0
            )

            with st.form("edit_resource_form"):
                new_name = st.text_input(
                    "Resource Name",
                    value=selected["name"]
                )

                new_category = st.selectbox(
                    "Category",
                    CATEGORIES,
                    index=category_index,
                    key="edit_resource_category"
                )

                new_department = st.text_input(
                    "Department",
                    value=selected["department"]
                )

                new_capacity = st.number_input(
                    "Capacity / Quantity",
                    min_value=1,
                    max_value=10000,
                    value=max(1, int(selected["capacity"] or 1))
                )

                new_specifications = st.text_area(
                    "Specifications",
                    value=selected["specifications"] or ""
                )

                new_guidelines = st.text_area(
                    "Usage Guidelines",
                    value=selected["guidelines"] or ""
                )

                save = st.form_submit_button(
                    "Save Changes",
                    use_container_width=True
                )

                if save:
                    success, message = db.update_resource(
                        selected["id"],
                        new_name,
                        new_category,
                        new_department,
                        int(new_capacity),
                        new_specifications,
                        new_guidelines
                    )

                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

        else:
            st.info("No resources available to edit.")

    # DELETE RESOURCE
    with delete_tab:
        resources = db.get_resources()

        if resources:
            resource_map = {
                f'{r["name"]} (ID: {r["id"]})': r
                for r in resources
            }

            selected_label = st.selectbox(
                "Choose resource to delete",
                list(resource_map.keys()),
                key="delete_resource_choice"
            )

            selected = resource_map[selected_label]

            st.warning(
                f"You selected: {selected['name']}. "
                "Resources with booking records cannot be deleted."
            )

            confirm = st.checkbox(
                "I confirm that I want to delete this resource.",
                key="confirm_resource_deletion"
            )

            if st.button(
                "Delete Resource",
                key="delete_resource_button",
                use_container_width=True
            ):
                if confirm:
                    success, message = db.delete_resource(selected["id"])

                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please confirm deletion first.")

        else:
            st.info("No resources available to delete.")


def render_admin_panel():
    st.title("🛡️ Admin Dashboard")
    st.write("Manage campus resources, reservations and student requests.")

    all_bookings = db.get_all_bookings()

    pending = sum(1 for b in all_bookings if b["status"] == "Pending")
    approved = sum(1 for b in all_bookings if b["status"] == "Approved")
    rejected = sum(1 for b in all_bookings if b["status"] == "Rejected")
    cancelled = sum(1 for b in all_bookings if b["status"] == "Cancelled")

    resources = db.get_resources()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Resources", len(resources))
    c2.metric("Pending", pending)
    c3.metric("Approved", approved)
    c4.metric("Rejected", rejected)
    c5.metric("Cancelled", cancelled)

    tab1, tab2, tab3, tab4 = st.tabs([
        "Manage Resources",
        "Pending Requests",
        "All Bookings",
        "History Log"
    ])

    with tab1:
        render_resource_management()

    with tab2:
        st.subheader("Requests Awaiting Approval")

        pending_bookings = [
            b for b in all_bookings if b["status"] == "Pending"
        ]

        if not pending_bookings:
            st.success("There are no pending requests.")
        else:
            for booking in pending_bookings:
                with st.expander(
                    f"Booking #{booking['id']} — "
                    f"{booking['resource_name']} — "
                    f"{booking['student_name']}"
                ):
                    st.write("Student:", booking["student_name"])
                    st.write("Roll Number:", booking["roll_number"])
                    st.write("Section:", booking["section"])
                    st.write("Year:", booking["year"])
                    st.write("Mobile:", booking["mobile"])
                    st.write("Email:", booking["email"])
                    st.write("Category:", booking["category"])
                    st.write("Purpose:", booking["description"])
                    st.write("Date:", booking["booking_date"])
                    st.write(
                        "Time:",
                        f"{booking['start_time']} - {booking['end_time']}"
                    )
                    st.write("Submitted:", booking["created_at"])

                    with st.form(f"admin_review_{booking['id']}"):
                        note = st.text_area(
                            "Admin Note / Reason",
                            key=f"note_{booking['id']}",
                            placeholder="Explain the decision."
                        )

                        decision = st.radio(
                            "Decision",
                            ["Approve", "Reject"],
                            horizontal=True,
                            key=f"decision_{booking['id']}"
                        )

                        submitted = st.form_submit_button(
                            "Save Decision",
                            use_container_width=True
                        )

                        if submitted:
                            new_status = (
                                "Approved" if decision == "Approve"
                                else "Rejected"
                            )

                            success, message = db.update_booking_status(
                                booking["id"], new_status, note
                            )

                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)

    with tab3:
        st.subheader("All Reservation Records")

        status_filter = st.selectbox(
            "Filter by status",
            ["All", "Pending", "Approved", "Rejected", "Cancelled"]
        )

        filtered_bookings = db.get_all_bookings(status_filter)

        if filtered_bookings:
            rows = [
                {
                    "Booking ID": b["id"],
                    "Student": b["student_name"],
                    "Roll Number": b["roll_number"],
                    "Resource": b["resource_name"],
                    "Category": b["category"],
                    "Date": b["booking_date"],
                    "Start": b["start_time"],
                    "End": b["end_time"],
                    "Status": b["status"],
                    "Admin Note": b["admin_note"]
                }
                for b in filtered_bookings
            ]

            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No booking records found.")

    with tab4:
        st.subheader("Booking History and Audit Log")

        history = db.get_history()

        if history:
            rows = [
                {
                    "Booking ID": h["booking_id"],
                    "Student": h["student_name"],
                    "Roll Number": h["roll_number"],
                    "Resource": h["resource_name"],
                    "Action": h["action"],
                    "Note": h["note"],
                    "Date/Time": h["changed_at"]
                }
                for h in history
            ]

            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True,
                hide_index=True
            )

            csv_data = pd.DataFrame(rows).to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                "Download History as CSV",
                data=csv_data,
                file_name="campus_booking_history.csv",
                mime="text/csv"
            )
        else:
            st.info("No history available.")
