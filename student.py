
import streamlit as st
import pandas as pd
from datetime import date, time, datetime

import database as db


def render_student_panel():
    st.title("🎓 Student Panel")
    st.write("Explore campus resources and manage your bookings.")

    tab1, tab2, tab3 = st.tabs([
        "Resource Directory",
        "Book a Resource",
        "My Dashboard"
    ])

    with tab1:
        st.subheader("Available Campus Resources")

        category = st.selectbox(
            "Choose category",
            ["All", "Equipment", "Room", "Lab", "Auditorium"],
            key="student_resource_category"
        )

        departments = ["All"] + db.get_departments()
        department = st.selectbox(
            "Choose department",
            departments,
            key="student_resource_department"
        )

        resources = db.get_resources(category, department)

        if resources:
            for resource in resources:
                with st.expander(
                    f"{resource['name']} | {resource['category']}"
                ):
                    st.write("Department:", resource["department"])
                    st.write("Capacity / Quantity:", resource["capacity"])
                    st.write("Specifications:", resource["specifications"])
                    st.info("Guidelines: " + resource["guidelines"])
        else:
            st.info("No resources found.")

    with tab2:
        st.subheader("Submit a Booking Request")

        categories = ["Equipment", "Room", "Lab", "Auditorium"]
        chosen_category = st.selectbox(
            "Resource category",
            categories,
            key="booking_category"
        )

        resources = db.get_resources(chosen_category)

        if not resources:
            st.warning("No resources are available in this category.")
        else:
            resource_options = {
                f"{r['name']} — {r['department']}": r["id"]
                for r in resources
            }

            selected_resource = st.selectbox(
                "Select resource",
                list(resource_options.keys()),
                key="booking_resource"
            )

            resource_id = resource_options[selected_resource]
            resource = db.get_resource(resource_id)

            st.caption(
                f"Capacity/quantity: {resource['capacity']} | "
                f"Specifications: {resource['specifications']}"
            )
            st.info("Guidelines: " + resource["guidelines"])

            with st.form("booking_form"):
                st.markdown("### Student Information")

                student_name = st.text_input("Full Name")
                roll_number = st.text_input("Roll Number")
                section = st.text_input("Section")
                year = st.selectbox(
                    "Year of Study",
                    ["1st Year", "2nd Year", "3rd Year", "4th Year"]
                )

                mobile = st.text_input("Mobile Number")
                email = st.text_input("Email ID")

                st.markdown("### Booking Information")

                booking_date = st.date_input(
                    "Booking Date",
                    value=date.today(),
                    min_value=date.today()
                )

                col1, col2 = st.columns(2)

                with col1:
                    start_time = st.time_input(
                        "Start Time", value=time(10, 0)
                    )

                with col2:
                    end_time = st.time_input(
                        "End Time", value=time(11, 0)
                    )

                description = st.text_area(
                    "Purpose / Description",
                    placeholder=(
                        "Explain why you need this resource, "
                        "your project, expected usage, etc."
                    )
                )

                submitted = st.form_submit_button(
                    "Submit Booking Request",
                    use_container_width=True
                )

                if submitted:
                    if not all([
                        student_name.strip(),
                        roll_number.strip(),
                        section.strip(),
                        mobile.strip(),
                        email.strip(),
                        description.strip()
                    ]):
                        st.error("Please fill in all fields.")

                    elif not mobile.isdigit() or len(mobile) != 10:
                        st.error("Enter a valid 10-digit mobile number.")

                    elif "@" not in email or "." not in email.split("@")[-1]:
                        st.error("Enter a valid email address.")

                    elif start_time >= end_time:
                        st.error("End time must be later than start time.")

                    else:
                        data = {
                            "student_name": student_name.strip(),
                            "roll_number": roll_number.strip(),
                            "section": section.strip(),
                            "year": year,
                            "mobile": mobile.strip(),
                            "email": email.strip(),
                            "description": description.strip(),
                            "resource_id": resource_id,
                            "booking_date": booking_date.isoformat(),
                            "start_time": start_time.strftime("%H:%M"),
                            "end_time": end_time.strftime("%H:%M")
                        }

                        success, message = db.create_booking(data)

                        if success:
                            st.success(message)
                        else:
                            st.error(message)

    with tab3:
        st.subheader("My Booking Dashboard")

        roll = st.text_input(
            "Enter your Roll Number to view your bookings",
            key="dashboard_roll"
        )

        if st.button("View My Bookings"):
            if not roll.strip():
                st.warning("Please enter your roll number.")
            else:
                st.session_state["view_student_roll"] = roll.strip()

        dashboard_roll = st.session_state.get("view_student_roll", "")

        if dashboard_roll:
            bookings = db.get_student_bookings(dashboard_roll)

            if not bookings:
                st.info("No bookings found for this roll number.")
            else:
                for booking in bookings:
                    with st.expander(
                        f"#{booking['id']} — {booking['resource_name']} "
                        f"({booking['status']})"
                    ):
                        st.write("Student:", booking["student_name"])
                        st.write("Roll Number:", booking["roll_number"])
                        st.write("Section:", booking["section"])
                        st.write("Year:", booking["year"])
                        st.write("Email:", booking["email"])
                        st.write("Mobile:", booking["mobile"])
                        st.write("Purpose:", booking["description"])
                        st.write("Date:", booking["booking_date"])
                        st.write(
                            "Time:",
                            f"{booking['start_time']} - {booking['end_time']}"
                        )
                        st.write("Status:", booking["status"])
                        st.write(
                            "Admin Note:",
                            booking["admin_note"] or "No note yet."
                        )

                        if booking["status"] in ("Pending", "Approved"):
                            if st.button(
                                "Cancel Booking",
                                key=f"cancel_{booking['id']}"
                            ):
                                ok, message = db.cancel_booking(
                                    booking["id"], dashboard_roll
                                )

                                if ok:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)

            st.markdown("### Booking History")
            history_rows = db.get_history()
            my_history = [
                {
                    "Booking ID": h["booking_id"],
                    "Resource": h["resource_name"],
                    "Action": h["action"],
                    "Note": h["note"],
                    "Date/Time": h["changed_at"]
                }
                for h in history_rows
                if h["roll_number"].strip().lower()
                == dashboard_roll.strip().lower()
            ]

            if my_history:
                st.dataframe(
                    pd.DataFrame(my_history),
                    use_container_width=True,
                    hide_index=True
                )
