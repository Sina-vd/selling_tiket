import json

class Event:
    def __init__(self, title, capacity, date):
        self.title = title
        self.total_capacity = capacity
        self.remaining_capacity = capacity
        self.date = date
        self.reserved_national_ids = []

class Ticket:
    def __init__(self, national_id, event_title, date, status="pending"):
        self.national_id = national_id
        self.event_title = event_title
        self.date = date
        self.status = status

def save_events_to_file(events, filename="events.json"):
    data = [{
        "title": e.title,
        "total_capacity": e.total_capacity,
        "remaining_capacity": e.remaining_capacity,
        "date": e.date,
        "reserved_national_ids": e.reserved_national_ids
    } for e in events]
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def load_events_from_file(filename="events.json"):
    try:
        with open(filename, "r",) as f:
            data = json.load(f)
            events = []
            for e in data:
                event = Event(e["title"], e["total_capacity"], e["date"])
                event.remaining_capacity = e["remaining_capacity"]
                event.reserved_national_ids = e["reserved_national_ids"]
                events.append(event)
            return events
    except FileNotFoundError:
        return []

def save_tickets_to_file(tickets, filename="tickets.json"):
    data = [{
        "national_id": t.national_id,
        "event_title": t.event_title,
        "date": t.date,
        "status": t.status
    } for t in tickets]
    with open(filename, "w",) as f:
        json.dump(data, f, indent=4)

def load_tickets_from_file(filename="tickets.json"):
    try:
        with open(filename, "r",) as f:
            data = json.load(f)
            return [Ticket(t["national_id"], t["event_title"], t["date"], t["status"]) for t in data]
    except FileNotFoundError:
        return []

class Manager:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.events = load_events_from_file()
        self.admin_is_logged_in = False

    def create_event(self, title, capacity, date):
        event = Event(title, capacity, date)
        self.events.append(event)
        save_events_to_file(self.events)
        print(f"Event '{title}' created.")

    def list_events(self):
        if not self.events:
            print("No events available.")
        for idx, event in enumerate(self.events, 1):
            print(f"{idx}. {event.title} | {event.date} | Remaining: {event.remaining_capacity}")

    def report(self):
        tickets = load_tickets_from_file()
        print("Ticket Report:")
        for event in self.events:
            sold = sum(1 for t in tickets if t.event_title == event.title and t.status == "confirmed")
            print(f"- {event.title}: Sold: {sold} | Remaining: {event.remaining_capacity}")

    def verify_admin_login(self, username, password):
        return username == self.username and password == self.password

    def generate_sales_report(self):
        self.report()

    def view_my_tickets(self, national_id):
        tickets = load_tickets_from_file()
        user_tickets = [t for t in tickets if t.national_id == national_id]
        if not user_tickets:
            print("You have no tickets.")
        for ticket in user_tickets:
            print(f"Ticket for {ticket.event_title} on {ticket.date} - Status: {ticket.status}")

    def reserve_ticket(self, event_title, national_id):
        event = next((e for e in self.events if e.title == event_title), None)
        if not event:
            print("Event not found.")
        elif national_id in event.reserved_national_ids:
            print("You have already reserved a ticket for this event.")
        elif event.remaining_capacity <= 0:
            print("No more tickets available for this event.")
        else:
            ticket = Ticket(national_id, event_title, event.date, "pending")
            event.reserved_national_ids.append(national_id)
            event.remaining_capacity -= 1
            save_events_to_file(self.events)
            tickets = load_tickets_from_file()
            tickets.append(ticket)
            save_tickets_to_file(tickets)
            print("Ticket reserved successfully.")

    def cancel_reservation(self, national_id):
        tickets = load_tickets_from_file()
        ticket = next((t for t in tickets if t.national_id == national_id and t.status == "pending"), None)
        if ticket:
            ticket.status = "canceled"
            print("Reservation canceled.")
            save_tickets_to_file(tickets)
        else:
            print("Ticket not found or already canceled.")

    def confirm_reservation(self, national_id):
        tickets = load_tickets_from_file()
        ticket = next((t for t in tickets if t.national_id == national_id and t.status == "pending"), None)
        if ticket:
            ticket.status = "confirmed"
            print("Reservation confirmed.")
            save_tickets_to_file(tickets)
        else:
            print("Ticket not found or already confirmed.")

def run():
    manager = Manager("sina", "1234")
    while True:
        print("\nWelcome to the Maktab 130 Reservation System")
        print("1. Admin Login")
        print("2. User Login")
        print("3. Exit")
        choice = input("Please enter your choice: ")

        if choice == '1':
            username = input("Admin Username: ")
            password = input("Admin Password: ")
            if manager.verify_admin_login(username, password):
                manager.admin_is_logged_in = True
                print("Login successful.")
                while manager.admin_is_logged_in:
                    print("\nAdmin Menu:")
                    print("1. Create New Event")
                    print("2. View All Events")
                    print("3. Sales Report")
                    print("4. Logout")
                    admin_choice = input("Please enter your choice: ")

                    if admin_choice == '1':
                        title = input("Event Title: ")
                        capacity = int(input("Total Capacity: "))
                        date = input("Event Date (YYYY-MM-DD): ")
                        manager.create_event(title, capacity, date)
                    elif admin_choice == '2':
                        manager.list_events()
                    elif admin_choice == '3':
                        manager.generate_sales_report()
                    elif admin_choice == '4':
                        manager.admin_is_logged_in = False
                        print("Logged out from admin account.")
                    else:
                        print("Invalid option.")
            else:
                print("Incorrect username or password.")

        elif choice == '2':
            national_id = input("Enter your National ID: ")
            while True:
                print("\nUser Menu:")
                print("1. View My Tickets")
                print("2. Reserve Ticket")
                print("3. Cancel Reservation")
                print("4. Confirm Reservation")
                print("5. View All Events")
                print("6. Switch User")
                print("7. Exit")
                user_choice = input("Please enter your choice: ")

                if user_choice == '1':
                    manager.view_my_tickets(national_id)

                elif user_choice == '2':
                    print("\nAvailable Events:")
                    if not manager.events:
                        print("No events available.")
                        continue

                    for idx, event in enumerate(manager.events, 1):
                        print(f"{idx}. {event.title} | {event.date} | Remaining: {event.remaining_capacity}")

                    try:
                        event_index = int(input("Enter the number of the event you want to reserve: ")) - 1
                        if 0 <= event_index < len(manager.events):
                            selected_event = manager.events[event_index]
                            manager.reserve_ticket(selected_event.title, national_id)
                        else:
                            print("Invalid event number.")
                    except ValueError:
                        print("Please enter a valid number.")

                elif user_choice == '3':
                    manager.cancel_reservation(national_id)

                elif user_choice == '4':
                    manager.confirm_reservation(national_id)

                elif user_choice == '5':
                    manager.list_events()

                elif user_choice == '6':
                    print("Switching user.")
                    break

                elif user_choice == '7':
                    print("Exiting user account.")
                    return

                else:
                    print("Invalid option.")

        elif choice == '3':
            print("Exiting the system. Goodbye!")
            break
        else:
            print("Invalid option.")
run()
