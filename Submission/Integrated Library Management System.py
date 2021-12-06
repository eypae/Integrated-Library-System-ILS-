from tkinter import *
from PIL import ImageTk,Image
from datetime import *
import pymongo
import mysql.connector as mysql
from tkinter import messagebox
import secrets


#Global variables
#root => main window
#editor => new window
#editor2 => window for registration
#user_login_input => userid
#password_login_input => user password
#userid_registration => id for registration
#password_registration => password for registration
#passwordconfirm_registration => password confirmation for registration


mysqlpassword = input(str("Enter mySQL password : "))  #enter mySQL password
root = Tk()
root.title("Integrated Library Management System Login Page")
root.geometry("700x700")
#admin user registration
admin = [("admin", "password"),]


# Cancel reservation function
def cancelReservation():
    global cancelReservation

    # Connecting to MySQL Database
    db = mysql.connect(host="localhost",
                       user="root",
                       password=mysqlpassword,
                       database="ils2",
                       autocommit=True)
    command_handler = db.cursor(buffered=True)

    reservation_to_cancel = bookID_to_act_on.get()

    # check whether book has been reserved by user
    command_handler.execute("SELECT COUNT(1) FROM ReserveStatus WHERE BookID = %s AND UserID = %s",\
                            (reservation_to_cancel, user_login_input))
    result = command_handler.fetchone()[0]

    if result:
        command_handler.execute("DELETE FROM ReserveStatus WHERE bookID = %s", (reservation_to_cancel,))
        return messagebox.showinfo(message= "Reservation for book " + reservation_to_cancel + " has been cancelled")
    else:
        return messagebox.showinfo(message= "This book is not under your reservations")

# Extend book function
def extendBook():
    global extendBook

    # Connecting to MySQL Database
    db = mysql.connect(host="localhost",
                       user="root",
                       password=mysqlpassword,
                       database="ils2",
                       autocommit=True)
    command_handler = db.cursor(buffered=True)

    book_to_extend = bookID_to_act_on.get()
    
    # check whether user has fines
    command_handler.execute("SELECT FineDateTime, FineAmount FROM Fine WHERE UserID = %s", (user_login_input,))
    fines_output = command_handler.fetchall()

    # check if book borrowed by user
    command_handler.execute("SELECT ExpectedDueDate, ExtensionStatus FROM LoanStatus WHERE userID = %s AND bookID = %s", (user_login_input, book_to_extend))
    books_output = command_handler.fetchone()

    # check if book has already been reserved
    command_handler.execute("SELECT COUNT(1) FROM ReserveStatus WHERE bookID = %s", (book_to_extend,))
    reserve_output = command_handler.fetchone()[0]  
    
    # update extension if not already extended
    if fines_output:
        return messagebox.showinfo(message="Sorry, unable to extend books as you have outstanding fines.")
    elif not books_output:
        return messagebox.showinfo(message="Book is not borrowed by you")
    elif reserve_output:
        return messagebox.showinfo(message="Book has already been reserved by another user")
    else:
        # check if books extended before
        if not books_output[1]:
            command_handler.execute("UPDATE LoanStatus SET ExpectedDueDate = %s, ExtensionStatus = %s WHERE bookID = %s",\
                                    ((books_output[0] +  timedelta(days = 28)).strftime('%Y-%m-%d %H:%M:%S'),\
                                     True, book_to_extend))
            return messagebox.showinfo(message= "Book " + book_to_extend + " has been extended by 4 weeks")
        else:
            return messagebox.showinfo(message="Book you have selected has already been extended")
            

# return book function
def returnBook():
    global returnBook

    # Connecting to MySQL Database
    db = mysql.connect(host="localhost",
                       user="root",
                       password=mysqlpassword,
                       database="ils2",
                       autocommit=True)
    command_handler = db.cursor(buffered=True)

    book_to_return = bookID_to_act_on.get()

    # check whether book is actually borrowed by user
    command_handler.execute("SELECT COUNT(1) FROM LoanStatus WHERE BookID = %s AND UserID = %s",\
                            (book_to_return, user_login_input))
    result = command_handler.fetchone()[0]

    # if true then update
    if result:
        command_handler.execute("DELETE FROM LoanStatus WHERE UserID = %s AND bookID = %s", \
                                (user_login_input, book_to_return))

        # check if book was overdue
        
        
        return messagebox.showinfo(message="Book has been successfully returned.")
    else:
        return messagebox.showinfo(message="Book is not currently borrowed by you")



# button to view your loans/reserves from manage books page
def view_loans_and_reserves():
    global borrow_listings
    global reserve_listings

    # To show all borrowed and reserved books
    command_handler.execute(\
        "SELECT T1.BookID, T2.Title, T1.ExpectedDueDate FROM LoanStatus as T1 INNER JOIN Book AS T2 ON T1.BookID = T2.BookID WHERE UserID = %s", (user_login_input,))
    borrowed_books = command_handler.fetchall()

    command_handler.execute(\
        "SELECT T1.BookID, T2.Title, T1.ReserveDate FROM ReserveStatus as T1 INNER JOIN Book AS T2 ON T1.BookID = T2.BookID WHERE UserID = %s", (user_login_input,))
    reserved_books = command_handler.fetchall()

    if not (borrowed_books or reserved_books):
        messagebox.showwarning(message="You have not borrowed or reserved any books!")
    else:
        if borrowed_books:
            borrow_listings = Toplevel()
            borrow_listings.title("Borrowed books")
            borrow_listings.geometry("700x700")
            row_counter = 1

            #column headings
            e1 = Entry(borrow_listings, width=35, fg="blue")
            e1.grid(row=0, column=0)
            e1.insert(END, "Book ID:")
            e2 = Entry(borrow_listings, width=35, fg="blue")
            e2.grid(row=0, column=1)
            e2.insert(END, "Book Title: ")
            e3 = Entry(borrow_listings, width=35, fg="blue")
            e3.grid(row=0, column=2)
            e3.insert(END, "Book Due Date: ")
            
            for one_book in borrowed_books:
                for j in range(len(one_book)):
                    e = Entry(borrow_listings, width=35, fg="blue")
                    e.grid(row=row_counter, column=j)
                    entry = str(one_book[j])
                    e.insert(END, entry)
                row_counter += 1
                
        if reserved_books:
            reserve_listings = Toplevel()
            reserve_listings.title("Reserved books")
            reserve_listings.geometry("700x700")
            row_counter = 1

            #column headings
            e4 = Entry(reserve_listings, width=35, fg="blue")
            e4.grid(row=0, column=0)
            e4.insert(END, "Book ID:")
            e5 = Entry(reserve_listings, width=35, fg="blue")
            e5.grid(row=0, column=1)
            e5.insert(END, "Book Title:")
            e6 = Entry(reserve_listings, width=35, fg="blue")
            e6.grid(row=0, column=2)
            e6.insert(END, "Reserve Date:")
            
            for one_book in reserved_books:
                for j in range(len(one_book)):
                    e = Entry(reserve_listings, width=35, fg="blue")
                    e.grid(row=row_counter, column=j)
                    entry = str(one_book[j])
                    e.insert(END, entry)
                row_counter += 1

                
# Manage books/reservations
def manage_books():
    editor.withdraw()
    global manage

    def main_page():
        manage.destroy()
        try:
            borrow_listings.withdraw()
        except:
            pass
        try:
            reserve_listings.withdraw()
        except:
            pass
        editor.deiconify()
        
    # Connecting to MySQL Database
    db = mysql.connect(host="localhost",
                       user="root",
                       password=mysqlpassword,
                       database="ils2",
                       autocommit=True)
    command_handler = db.cursor(buffered=True)  
    
    manage = Toplevel()
    manage.title("Manage Books & Reservations")
    manage.minsize(width=400, height=700)
    manage.geometry("700x700")

    bg_n, check_bg = 0.25, True

    #Background image
    login_img = Image.open("lib.jpg")       
    [img_width, img_height] = login_img.size
    login_n, check_login = 0.25, True
    new_img_width = int(img_width * login_n)
    if check_login:
        new_img_height = int (img_height * login_n)
    else:
        new_img_height = int (img_height / login_n)

    login_img = login_img.resize((3000,1400),Image.ANTIALIAS)
    img = ImageTk.PhotoImage(login_img)
    Canvas1 = Canvas(manage)
    Canvas1.create_image(300,340,image = img)      
    Canvas1.config(bg="white",width = new_img_width, height = new_img_height)
    Canvas1.pack(expand=True,fill=BOTH)


    # Implementing Label
    headingFrame1 = Frame(manage, bg="#FFBB00", bd=5)
    headingFrame1.place(relx=0.2, rely=0.1, relwidth=0.6, relheight=0.18)
    headingLabel = Label(headingFrame1, text="Manage books and reservations", bg='brown', fg='white', font=('Calibri', 20))
    headingLabel.place(relx=0, rely=0, relwidth=1, relheight=1)

    # Implementing book return/extend/cancel reservation label and text box
    return_label = Label(manage, \
                         text="Input Book ID of the book you are returning / extending / cancelling reservation for",\
                         font=('Calibri', 10, 'underline'))
    return_label.place(relx=0.15, rely=0.40, relwidth=0.70, relheight=0.05)

    # all 3 buttons will act on this input book ID
    global bookID_to_act_on
    bookID_to_act_on = Entry(manage, width=30)
    bookID_to_act_on.place(relx=0.28, rely=0.50, relwidth=0.45, relheight=0.04)

    return_button = Button(manage, text="Return Book", bg='cadetblue', fg='white', command=returnBook)
    return_button.place(relx=0.2, rely=0.55, relwidth=0.20, relheight=0.05)
    
    extend_button = Button(manage, text="Extend Book", bg='cadetblue', fg='white', command=extendBook)
    extend_button.place(relx=0.40, rely=0.55, relwidth=0.20, relheight=0.05)

    cancel_button = Button(manage, text="Cancel Reservation", bg='cadetblue', fg='white', command=cancelReservation)
    cancel_button.place(relx=0.6, rely=0.55, relwidth=0.20, relheight=0.05)

    # view books button
    view_books_button = Button(manage, text = "View my current loans and reserves", bg='darkblue', fg='white', command=view_loans_and_reserves)
    view_books_button.place(relx=0.28, rely=0.70, relwidth=0.45, relheight=0.08)

    # previous button
    previous = Button(manage, text="Go back to user menu", bg='cadetblue', fg='white', command=main_page)
    previous.place(relx=0.28, rely=0.85, relwidth=0.45, relheight=0.08)

    manage.mainloop()


#Check for overdue books and update SQL system
def update_fines():
    db = mysql.connect(host="localhost",
                   user="root",
                   password = mysqlpassword,  
                   database="ils2",
                   autocommit = True)
    command_handler = db.cursor(buffered=True)
    command_handler.execute("SELECT UserID, ExpectedDueDate FROM LoanStatus")
    output = command_handler.fetchall()

    if not output:
        return

    for result in output:
        fine = 0
        due_date = result[1]
        user = result[0]
        date_difference = (datetime.now() - due_date).days
        command_handler = db.cursor(buffered=True)
        command_handler.execute("SELECT FineDateTime FROM Fine WHERE UserID = %s", (user,))
        user_data = command_handler.fetchall()
        if date_difference > 0:
            fine = date_difference
            try:
                if (due_date,) not in user_data:
                    raise Exception
                command_handler = db.cursor(buffered=True)
                command_handler.execute("UPDATE Fine SET FineAmount = %s WHERE UserID = %s AND FineDateTime = %s", (fine, user, due_date))
                command_handler = db.cursor(buffered=True)
                command_handler.execute("DELETE FROM ReserveStatus WHERE UserID = %s", (user,))
            except:
                command_handler = db.cursor(buffered=True)
                command_handler.execute("INSERT INTO Fine (UserID, FineDateTime, FineAmount) VALUES (%s,%s,%s)",
                                        (user, due_date, fine))
                command_handler = db.cursor(buffered=True)
                command_handler.execute("DELETE FROM ReserveStatus WHERE UserID = %s", (user,))
                

#Payment transaction history
def transaction_view():
    global transactions

    db = mysql.connect(host="localhost",
                   user="root",
                   password = mysqlpassword,  
                   database="ils2",
                   autocommit = True)
    command_handler = db.cursor(buffered=True)

    def main_page():
        transactions.destroy()
        payments.deiconify()

    try:
        command_handler.execute("SELECT PaymentID, PaymentDateTime, PaymentAmount FROM payment WHERE UserID = %s ORDER BY PaymentDateTime desc", (user_login_input,))
        output = command_handler.fetchall()
        if not output:
            return messagebox.showinfo(message = "No transaction history found!")
        else:
            question = messagebox.askyesnocancel(message = "Transaction history found, would you like to proceed?")

            if question:
                transactions = Toplevel()
                transactions.title("Transaction History")
                transactions.geometry("1000x250")
                row_counter = 1
                #column headings
                e1 = Entry(transactions, width=30, fg="blue")
                e1.grid(row=0, column=0)
                e1.insert(END, "Payment ID:")
                e2 = Entry(transactions, width=30, fg="blue")
                e2.grid(row=0, column=1)
                e2.insert(END, "Fine paid at: ")
                e3 = Entry(transactions, width=30, fg="blue")
                e3.grid(row=0, column=2)
                e3.insert(END, "Amount paid: $")               
                for lib_entry in output:
                    for j in range(len(lib_entry)):
                        e = Entry(transactions, width = 30, fg = "blue")
                        e.grid(row = row_counter, column = j)
                        entry = str(lib_entry[j])
                        e.insert(END, entry)
                    row_counter += 1
            else:
                return
    except:
        return messagebox.showwarning(message = "No transaction history found!")
    

#generate unique paymentID
def generate_paymentID():
    hexstr = secrets.token_hex(4)
    paymentid = int(hexstr, 16)
    return str(paymentid)

#paying single fine
def pay_single():
    payment.withdraw()
    global payment_single

    db = mysql.connect(host="localhost",
                   user="root",
                   password = mysqlpassword,  
                   database="ils2",
                   autocommit = True)
    command_handler = db.cursor(buffered=True)
    command_handler.execute("SELECT FineDateTime, FineAmount FROM Fine WHERE UserID = %s", (user_login_input,))
    output = command_handler.fetchall()
    

    def show_fine():
        global single_fines_view
        single_fines_view = Toplevel()
        single_fines_view.title("Outstanding Fines")
        single_fines_view.geometry("600x250")
        row_counter = 1
        e1 = Entry(single_fines_view, width=50, fg="blue")
        e1.grid(row=0, column=0)
        e1.insert(END, "S/N: ")
        e2 = Entry(single_fines_view, width=50, fg="blue")
        e2.grid(row=0, column=1)
        e2.insert(END, "Amount: $")
        for lib_entry in output:
            for j in range(len(lib_entry)):
                e = Entry(single_fines_view, width = 50, fg = "blue")
                e.grid(row = row_counter, column = j)
                if j == 0:
                    entry = str(row_counter) + ") " + str(lib_entry[j])
                else:
                    entry = str(lib_entry[j])
                e.insert(END, entry)
            row_counter += 1
        
    
    show_fine()
    payment_single = Toplevel()
    payment_single.title("Transaction Page")
    payment_single.geometry("500x200")

    #Creating Label
    Label(payment_single, text = "S/N of fine:").grid(row = 0)
    Label(payment_single, text = "Credit/Debit Card Number: ").grid(row = 1)
    Label(payment_single, text = "MM/YY: ").grid(row = 2)
    Label(payment_single, text = "CVV: ").grid(row = 3)

    #Creating Payment Entry
    number_entry = Entry(payment_single)
    creditcard_entry = Entry(payment_single)
    number_entry.grid(row = 0, column = 1)
    creditcard_entry = Entry(payment_single)
    creditcard_entry.grid(row = 1, column = 1)
    dateyear_entry = Entry(payment_single)
    dateyear_entry.grid(row = 2, column = 1)
    cvv_entry = Entry(payment_single)
    cvv_entry.grid(row = 3, column = 1)


    def confirm_payment():
        if (number_entry.get() == "") or (creditcard_entry.get() == "") or (dateyear_entry.get() == "") or (cvv_entry.get() == ""):
            messagebox.showwarning(message = "Invalid input! Please enter details")
            return

        try:
            user_input_no = int(number_entry.get()) - 1
            amount, date_time = str(output[user_input_no][1]), output[user_input_no][0]

            #Update payment
            command_handler = db.cursor(buffered=True)
            command_handler.execute("INSERT INTO payment (PaymentID, UserID, PaymentDateTime, PaymentAmount, FineDateTime, FineUserID) VALUES (%s,%s,%s,%s,%s,%s)",
                                    (generate_paymentID(), user_login_input, datetime.now(), amount, date_time, user_login_input))

            #Delete fines
            command_handler = db.cursor(buffered=True)
            command_handler.execute("DELETE FROM Fine WHERE UserID = %s AND FineDateTime = %s", (user_login_input, date_time))

            messagebox.showinfo(message = ("Payment Success for Fine: " + "Total amount owed: $" + amount + ", fine incurred at: ", date_time))
            single_fines_view.destroy()
            payment_single.destroy()
            fines.deiconify()
                        
        except:
            messagebox.showwarning(message = "Invalid S/N! Please try again")  
            
            

    def return_payment():
        single_fines_view.destroy()
        payment_single.destroy()
        payment.deiconify()
        

    #Creating Payment Button
    Button(payment_single, text = "Pay fines", command = confirm_payment).grid(row = 5, column = 0, sticky= W, pady = 4)
    Button(payment_single, text = "Return to previous page", command = return_payment).grid(row = 5, column = 1, sticky= W, pady = 4)
    
#paying all fines
def pay_all():
    db = mysql.connect(host="localhost",
                   user="root",
                   password = mysqlpassword,  
                   database="ils2",
                   autocommit = True)
    command_handler = db.cursor(buffered=True)
    command_handler.execute("SELECT FineDateTime, FineAmount FROM Fine WHERE UserID = %s", (user_login_input,))
    output = command_handler.fetchall()
    payment.withdraw()
    payment_all = Toplevel()
    payment_all.title("Transaction Page")
    payment_all.geometry("500x200")

    def return_payment():
        payment_all.destroy()
        payment.deiconify()

    def confirm_payment():
        if (creditcard_entry.get() == "") or (dateyear_entry.get() == "") or (cvv_entry.get() == ""):
            messagebox.showwarning(message = "Invalid input! Please enter details")
            return

        amount = str(sum(fine[1] for fine in output))
        for i in range(len(output)):
            date_time = output[i][0]
            amount_individual = output[i][1]

            #Update payment
            command_handler = db.cursor(buffered=True)
            command_handler.execute("INSERT INTO payment (PaymentID, UserID, PaymentDateTime, PaymentAmount, FineDateTime, FineUserID) VALUES (%s,%s,%s,%s,%s,%s)",
                                    (generate_paymentID(), user_login_input, datetime.now(), amount_individual, date_time, user_login_input))
            
            
            #Update fines
            command_handler = db.cursor(buffered=True)
            command_handler.execute("DELETE FROM Fine WHERE UserID = %s AND FineDateTime = %s", (user_login_input, date_time))
            
        messagebox.showinfo(message = ("Payment Success for all fines: " + "Total amount paid: $" + amount))
        payment_all.destroy()
        fines.deiconify()


    #Creating Label
    Label(payment_all, text = ("Total amount of fines incurred: ")).grid(row = 0, column = 0)
    Label(payment_all, text = ("$" + str(sum(fine[1] for fine in output)))).grid(row = 0, column = 1)
    Label(payment_all, text = "Credit/Debit Card Number: ").grid(row = 1)
    Label(payment_all, text = "MM/YY: ").grid(row = 2)
    Label(payment_all, text = "CVV: ").grid(row = 3)
    
    #Creating Payment Entry
    creditcard_entry = Entry(payment_all)
    creditcard_entry = Entry(payment_all)
    creditcard_entry.grid(row = 1, column = 1)
    dateyear_entry = Entry(payment_all)
    dateyear_entry.grid(row = 2, column = 1)
    cvv_entry = Entry(payment_all)
    cvv_entry.grid(row = 3, column = 1)

    #Creating Payment Button
    Button(payment_all, text = "Pay all fines", command = confirm_payment).grid(row = 5, column = 0, sticky= W, pady = 4)
    Button(payment_all, text = "Return to previous page", command = return_payment).grid(row = 5, column = 1, sticky= W, pady = 4)
    

#payments page
def payments():
    db = mysql.connect(host="localhost",
                   user="root",
                   password = mysqlpassword,  
                   database="ils2",
                   autocommit = True)
    command_handler = db.cursor(buffered=True)
    try:
        command_handler.execute("SELECT FineDateTime, FineAmount FROM Fine WHERE UserID = %s", (user_login_input,))
        output = command_handler.fetchall()
        if not output:
            return messagebox.showinfo(message = "No outstanding fines found, no payment required!")

    except:
        return messagebox.showinfo(message = "No outstanding fines found, no payment required!")
    
    command_handler.execute("SELECT UserID, ExpectedDueDate FROM LoanStatus")
    checker = command_handler.fetchall()
    
    for result in checker:
        due_date = result[1]
        user = result[0]
        date_difference = (datetime.now() - due_date).days
        if date_difference > 28:
            return messagebox.showwarning(message = "Please return overdue books before making payment!")
            
    fines.withdraw()
    global payment

    def previous_page():
        payment.destroy()
        fines.deiconify()

    payment = Toplevel()
    payment.title("Payment of Fines")
    payment.minsize(width = 400, height = 700)
    payment.geometry("700x700")

    bg_n, check_bg = 0.25, True

    #Background image
    login_img = Image.open("lib.jpg")       
    [img_width, img_height] = login_img.size
    login_n, check_login = 0.25, True
    new_img_width = int(img_width * login_n)
    if check_login:
        new_img_height = int (img_height * login_n)
    else:
        new_img_height = int (img_height / login_n)

    login_img = login_img.resize((3000,1400),Image.ANTIALIAS)
    img = ImageTk.PhotoImage(login_img)
    Canvas1 = Canvas(payment)
    Canvas1.create_image(300,340,image = img)      
    Canvas1.config(bg="white",width = new_img_width, height = new_img_height)
    Canvas1.pack(expand=True,fill=BOTH)

    #Implementing Label
    paymentFrame = Frame(payment,bg="#FFBB00",bd=5)
    paymentFrame.place(relx=0.2,rely=0.1,relwidth=0.6,relheight=0.18)
    paymentLabel = Label(paymentFrame, text="Payments", bg='brown', fg='white', font=('Calibri',20))
    paymentLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

    #Adding Button
    pay_single_fine = Button(payment,text="Pay Single Fine",bg='cadetblue', fg='white', command = pay_single)
    pay_single_fine.place(relx=0.28,rely=0.40, relwidth=0.45,relheight=0.08)
    pay_all_fines = Button(payment,text="Pay All Outstanding Fines",bg='cadetblue', fg='white', command = pay_all)
    pay_all_fines.place(relx=0.28,rely=0.60, relwidth=0.45,relheight=0.08)
    return_page = Button(payment,text="Return to Previous Page",bg='red', fg='white', command = previous_page)
    return_page.place(relx=0.28,rely=0.80, relwidth=0.45,relheight=0.08)

    payment.mainloop()
    
#viewing of fines     
def view_fines_page():
    global view_fines

    db = mysql.connect(host="localhost",
                   user="root",
                   password = mysqlpassword,  
                   database="ils2",
                   autocommit = True)
    command_handler = db.cursor(buffered=True)
    try:
        command_handler.execute("SELECT FineDateTime, FineAmount FROM Fine WHERE UserID = %s", (user_login_input,))
        output = command_handler.fetchall()
        if not output:
            return messagebox.showinfo(message = "No outstanding fines!")
        else:
            question = messagebox.askyesnocancel(message = "Outstanding fines found, would you like to proceed?")

            if question:
                view_fines = Toplevel()
                view_fines.title("Outstanding Fines")
                view_fines.geometry("600x250")
                row_counter = 1
                #column headings
                e1 = Entry(view_fines, width=50, fg="blue")
                e1.grid(row=0, column=0)
                e1.insert(END, "Fines: ")
                e2 = Entry(view_fines, width=50, fg="blue")
                e2.grid(row=0, column=1)
                e2.insert(END, "Amount: $")  
                for lib_entry in output:
                    for j in range(len(lib_entry)):
                        e = Entry(view_fines, width = 50, fg = "blue")
                        e.grid(row = row_counter, column = j)
                        if j == 0:
                            entry = "S/N: " + str(row_counter) + ") " + str(lib_entry[j])
                        else:
                            entry = str(lib_entry[j])
                        e.insert(END, entry)
                    row_counter += 1
            else:
                return
    except:
        return messagebox.showwarning(message = "No outstanding fines!")
        


#fines and payment page
def fines_payment():
    editor.withdraw()
    global fines

    def main_page():
        fines.destroy()
        editor.deiconify()

    fines = Toplevel()
    fines.title("Fines and Payment")
    fines.minsize(width = 400, height = 700)
    fines.geometry("700x700")

    bg_n, check_bg = 0.25, True

    #Background image
    login_img = Image.open("lib.jpg")       
    [img_width, img_height] = login_img.size
    login_n, check_login = 0.25, True
    new_img_width = int(img_width * login_n)
    if check_login:
        new_img_height = int (img_height * login_n)
    else:
        new_img_height = int (img_height / login_n)

    login_img = login_img.resize((3000,1400),Image.ANTIALIAS)
    img = ImageTk.PhotoImage(login_img)
    Canvas1 = Canvas(fines)
    Canvas1.create_image(300,340,image = img)      
    Canvas1.config(bg="white",width = new_img_width, height = new_img_height)
    Canvas1.pack(expand=True,fill=BOTH)

    #Implementing Label
    fineFrame = Frame(fines,bg="#FFBB00",bd=5)
    fineFrame.place(relx=0.2,rely=0.1,relwidth=0.6,relheight=0.18)
    fineLabel = Label(fineFrame, text="Fines and Payments", bg='brown', fg='white', font=('Calibri',20))
    fineLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

    #Adding Button
    view_fines = Button(fines,text="View Outstanding Fines",bg='cadetblue', fg='white', command = view_fines_page)
    view_fines.place(relx=0.28,rely=0.40, relwidth=0.45,relheight=0.08)
    pay_fines = Button(fines,text="Pay Outstanding Fines",bg='cadetblue', fg='white', command = payments)
    pay_fines.place(relx=0.28,rely=0.55, relwidth=0.45,relheight=0.08)
    transaction_history = Button(fines,text="Transaction History",bg='cadetblue', fg='white', command = transaction_view)
    transaction_history.place(relx=0.28,rely=0.70, relwidth=0.45,relheight=0.08)
    main_page = Button(fines,text="Return to Main Page",bg='red', fg='white', command = main_page)
    main_page.place(relx=0.28,rely=0.85, relwidth=0.45,relheight=0.08)

    
    fines.mainloop()


#member registration authentication
def auth_member():
    global user_login_input
    global password_login_input
    
    user_login_input = user_login_entry.get()
    password_login_input = password_login.get()
    db = mysql.connect(host="localhost",
                   user="root",
                   password = mysqlpassword,  
                   database="ils2",
                   autocommit = True)
    command_handler = db.cursor(buffered=True)
    command_handler.execute("SELECT COUNT(1) FROM user WHERE UserID = %s AND Password = %s", (user_login_input, password_login_input))
    result = command_handler.fetchone()[0]
    if result == 1:
        messagebox.showinfo(message = "Login success!")
        editor.destroy()
        member_sess()
    else:
        messagebox.showwarning(message = ("Error: Member details not recognised! Proceed to register if new"))

#user registration authentication
def auth_registration():
    db = mysql.connect(host="localhost",
                   user="root",
                   password = mysqlpassword,  
                   database="ils2",
                   autocommit = True)
    command_handler = db.cursor(buffered=True)
    if passwordconfirm_registration.get() != password_registration.get():
        messagebox.showwarning(message = "Error password do not match!")

    else:
        values = (userid_registration.get(), password_registration.get(), full_name_registration.get())
        try:
            command_handler.execute("INSERT INTO user (userID, password, name) VALUES (%s,%s,%s)", values)
            db.commit()
            messagebox.showinfo(message = "Registration success!")
            editor.destroy()
            editor2.destroy()
            user_login_page()
        except mysql.IntegrityError as iError:
            messagebox.showwarning(message = ("Error: Duplicate/Invalid Username! Please try again"))
            
            
            
#user registration        
def register():
    global editor2
    editor2 = Toplevel()
    editor2.title("Registration Page")
    editor2.geometry("500x500")

    #Global variables for registration
    global userid_registration
    global password_registration
    global passwordconfirm_registration
    global full_name_registration

    #Registration Label
    registration_label = Label(editor2, text = "Registration Page", width = 25, font = ("bold", 20, "underline"))
    registration_label.place(x = 60, y = 53)
    userid_label = Label(editor2, text = "User ID:", width = 20, font = ("bold", 10))
    userid_label.place(x = 50, y = 130)
    user_name = Label(editor2, text = "Full Name:", width = 20, font = ("bold", 10))
    user_name.place(x = 50, y = 200)    
    userid_password = Label(editor2, text = "Password:", width = 20, font = ("bold", 10))
    userid_password.place(x = 50, y = 270)
    userid_password_confirmation = Label(editor2, text = "Confirm Password:", width = 20, font = ("bold", 10))
    userid_password_confirmation.place(x = 40, y = 340)

    #Registration Entry
    userid_registration = Entry(editor2)
    userid_registration.place(x = 200, y = 130)
    full_name_registration = Entry(editor2)
    full_name_registration.place(x = 200, y = 200)
    password_registration = Entry(editor2)
    password_registration.place(x = 200, y = 270)
    passwordconfirm_registration = Entry(editor2)
    passwordconfirm_registration.place(x = 200, y = 340)

    #Registration Button
    registration_button = Button(editor2, text = "Register", bg = "brown", fg = "white", width = 30, command = auth_registration)
    registration_button.place(x = 140, y = 450)
    

#User login page
def user_login_page():
    root.withdraw()
    global editor
    db = mysql.connect(host="localhost",
                   user="root",
                   password = mysqlpassword,  
                   database="ils2",
                   autocommit = True)
    command_handler = db.cursor(buffered=True)

    editor = Toplevel()
    editor.title("User Login Page")
    editor.minsize(width = 400, height = 700)
    editor.geometry("700x700")

    bg_n, check_bg = 0.25, True

    #Background image
    login_img = Image.open("lib.jpg")       
    [img_width, img_height] = login_img.size
    login_n, check_login = 0.25, True
    new_img_width = int(img_width * login_n)
    if check_login:
        new_img_height = int (img_height * login_n)
    else:
        new_img_height = int (img_height / login_n)

    login_img = login_img.resize((3000,1400),Image.ANTIALIAS)
    img = ImageTk.PhotoImage(login_img)
    Canvas1 = Canvas(editor)
    Canvas1.create_image(300,340,image = img)      
    Canvas1.config(bg="white",width = new_img_width, height = new_img_height)
    Canvas1.pack(expand=True,fill=BOTH)
  

    #Implementing Label
    headingFrame1 = Frame(editor,bg="#FFBB00",bd=5)
    headingFrame1.place(relx=0.2,rely=0.1,relwidth=0.6,relheight=0.18)
    headingLabel = Label(headingFrame1, text="User Login Page", bg='brown', fg='white', font=('Calibri',20))
    headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

    #Implementing User login label
    user_id_label = Label(editor, text="Enter UserID", font=('Calibri',10, 'underline'))
    user_id_label.place(relx=0.40,rely=0.35, relwidth=0.20,relheight=0.04)
    user_password_label = Label(editor, text="Enter Password", font=('Calibri',10, 'underline'))
    user_password_label.place(relx=0.40,rely=0.50, relwidth=0.20,relheight=0.04)

    #Global variables for login text entry
    global user_login_entry
    global password_login

    #Text Boxes for Entry
    user_login_entry = Entry(editor, width = 30)
    user_login_entry.place(relx=0.28,rely=0.40, relwidth=0.45,relheight=0.04)
    password_login = Entry(editor, width = 30)
    password_login.place(relx=0.28,rely=0.55, relwidth=0.45,relheight=0.04)
    
    #Adding Button
    registration = Button(editor,text="Registration for new users",bg='cadetblue', fg='white', command = register)
    registration.place(relx=0.28,rely=0.80, relwidth=0.45,relheight=0.08)
    login_button = Button(editor,text="Login",bg='red', fg='white', command = auth_member)
    login_button.place(relx=0.28,rely=0.70, relwidth=0.45,relheight=0.08)

    editor.mainloop()

#Admin view all unpaid fines
def admin_view_fine():
    global admin_fines

    db = mysql.connect(host="localhost",
                   user="root",
                   password = mysqlpassword,  
                   database="ils2",
                   autocommit = True)
    command_handler = db.cursor(buffered=True)

    try:
        command_handler.execute("SELECT UserID, FineDateTime, FineAmount FROM Fine")
        output = command_handler.fetchall()
        if not output:
            return messagebox.showinfo(message = "No outstanding fines data found")
        else:
            question = messagebox.askyesnocancel(message = "Outstanding fines data found, would you like to proceed?")
            if question:
                admin_fines = Toplevel()
                admin_fines.title("Outstanding Fines Data")
                admin_fines.geometry("1000x250")
                row_counter = 1
                #column headings
                e1 = Entry(admin_fines, width=50, fg="blue")
                e1.grid(row=0, column=0)
                e1.insert(END, "User ID: ")
                e2 = Entry(admin_fines, width=50, fg="blue")
                e2.grid(row=0, column=1)
                e2.insert(END, "Fine incurred at at: ")
                e3 = Entry(admin_fines, width=50, fg="blue")
                e3.grid(row=0, column=2)
                e3.insert(END, "Amount owed: $")
                for lib_entry in output:
                    for j in range(len(lib_entry)):
                        e = Entry(admin_fines, width = 50, fg = "blue")
                        e.grid(row = row_counter, column = j)
                        entry = str(lib_entry[j])
                        e.insert(END, entry)
                    row_counter += 1
            else:
                return
    except:
        return messagebox.showwarning(message = "No past outstanding fines data found!")
    
#Admin view all reservation
def admin_view_reservation():
    global admin_reservation

    db = mysql.connect(host="localhost",
                   user="root",
                   password = mysqlpassword,  
                   database="ils2",
                   autocommit = True)
    command_handler = db.cursor(buffered=True)

    try:
        command_handler.execute("SELECT T1.BookID, T2.Title , T1.UserID, T1.ReserveDate FROM ReserveStatus AS T1 INNER JOIN Book AS T2 ON T1.BookID = T2.BookID ORDER BY BookID;")
        output = command_handler.fetchall()
        if not output:
            return messagebox.showinfo(message = "No past reservation data found")
        else:
            question = messagebox.askyesnocancel(message = "Reserved data found, would you like to proceed?")
            if question:
                admin_reservation = Toplevel()
                admin_reservation.title("Reserved Data")
                admin_reservation.geometry("1000x250")
                row_counter = 1
                #column headings
                e1 = Entry(admin_reservation, width=35, fg="blue")
                e1.grid(row=0, column=0)
                e1.insert(END, "Book ID:")
                e2 = Entry(admin_reservation, width=35, fg="blue")
                e2.grid(row=0, column=1)
                e2.insert(END, "Title: ")
                e3 = Entry(admin_reservation, width=35, fg="blue")
                e3.grid(row=0, column=2)
                e3.insert(END, "User ID: ")
                e4 = Entry(admin_reservation, width=35, fg="blue")
                e4.grid(row=0, column=3)
                e4.insert(END, "Reserve Date: ")  
                for lib_entry in output:
                    for j in range(len(lib_entry)):
                        e = Entry(admin_reservation, width = 35, fg = "blue")
                        e.grid(row = row_counter, column = j)
                        entry = str(lib_entry[j])
                        e.insert(END, entry)
                    row_counter += 1
            else:
                return
    except:
        return messagebox.showwarning(message = "No past reservation data found!")


    
#Admin view all borrowed books
def admin_view_books():
    global admin_books

    db = mysql.connect(host="localhost",
                   user="root",
                   password = mysqlpassword,  
                   database="ils2",
                   autocommit = True)
    command_handler = db.cursor(buffered=True)

    try:
        command_handler.execute("SELECT T1.BookID, T2.Title , T1.UserID, T1.ExpectedDueDate FROM LoanStatus AS T1 INNER JOIN Book AS T2 ON T1.BookID = T2.BookID ORDER BY BookID;")
        output = command_handler.fetchall()
        if not output:
            return messagebox.showinfo(message = "No past borrowing data found")
        else:
            question = messagebox.askyesnocancel(message = "Borrowing data found, would you like to proceed?")
            if question:
                admin_books = Toplevel()
                admin_books.title("Borrowing Data")
                admin_books.geometry("1000x250")
                row_counter = 1
                #column headings
                e1 = Entry(admin_books, width=35, fg="blue")
                e1.grid(row=0, column=0)
                e1.insert(END, "Book ID:")
                e2 = Entry(admin_books, width=35, fg="blue")
                e2.grid(row=0, column=1)
                e2.insert(END, "Title: ")
                e3 = Entry(admin_books, width=35, fg="blue")
                e3.grid(row=0, column=2)
                e3.insert(END, "User ID: ")
                e4 = Entry(admin_books, width=35, fg="blue")
                e4.grid(row=0, column=3)
                e4.insert(END, "Due Date: ")  
                for lib_entry in output:
                    for j in range(len(lib_entry)):
                        e = Entry(admin_books, width = 35, fg = "blue")
                        e.grid(row = row_counter, column = j)
                        entry = str(lib_entry[j])
                        e.insert(END, entry)
                    row_counter += 1
            else:
                return
    except:
        return messagebox.showwarning(message = "No past borrowing data found!")

#Admin session
def admin_sess_view():
    global admin_sess

    update_fines()
    admin_sess = Toplevel()
    admin_sess.title("Integrated Library Management System")
    admin_sess.minsize(width = 400, height = 700)
    admin_sess.geometry("700x700")

    def main_page():
        admin_sess.destroy()
        root.deiconify()
        

    bg_n, check_bg = 0.25, True

    #Background image
    login_img = Image.open("lib.jpg")       
    [img_width, img_height] = login_img.size
    login_n, check_login = 0.25, True
    new_img_width = int(img_width * login_n)
    if check_login:
        new_img_height = int (img_height * login_n)
    else:
        new_img_height = int (img_height / login_n)

    login_img = login_img.resize((3000,1400),Image.ANTIALIAS)
    img = ImageTk.PhotoImage(login_img)
    Canvas1 = Canvas(admin_sess)
    Canvas1.create_image(300,340,image = img)      
    Canvas1.config(bg="white",width = new_img_width, height = new_img_height)
    Canvas1.pack(expand=True,fill=BOTH)

    #Implementing Label
    headingFrame1 = Frame(admin_sess,bg="#FFBB00",bd=5)
    headingFrame1.place(relx=0.2,rely=0.1,relwidth=0.6,relheight=0.18)
    headingLabel = Label(headingFrame1, text="Admin Session", bg='brown', fg='white', font=('Calibri',20))
    headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

    #Adding Button
    view_borrowing = Button(admin_sess,text="View All Borrowings",bg='cadetblue', fg='white', command = admin_view_books)
    view_borrowing.place(relx=0.28,rely=0.40, relwidth=0.45,relheight=0.08)
    view_reservations = Button(admin_sess,text="View All Reservations",bg='cadetblue', fg='white', command = admin_view_reservation)
    view_reservations.place(relx=0.28,rely=0.55, relwidth=0.45,relheight=0.08)
    view_fines = Button(admin_sess,text="View all Unpaid Fines",bg='cadetblue', fg='white', command = admin_view_fine)
    view_fines.place(relx=0.28,rely=0.70, relwidth=0.45,relheight=0.08)
    logout = Button(admin_sess,text="Logout",bg='red', fg='white', command = main_page)
    logout.place(relx=0.28,rely=0.85, relwidth=0.45,relheight=0.08)
    
    admin_sess.mainloop()    
    

#Admin login page
def admin_login_page():
    root.withdraw()
    global admin_login

    admin_login = Toplevel()
    admin_login.title("Admin Login Page")
    admin_login.minsize(width = 400, height = 700)
    admin_login.geometry("700x700")

    bg_n, check_bg = 0.25, True

    #Background image
    login_img = Image.open("lib.jpg")       
    [img_width, img_height] = login_img.size
    login_n, check_login = 0.25, True
    new_img_width = int(img_width * login_n)
    if check_login:
        new_img_height = int (img_height * login_n)
    else:
        new_img_height = int (img_height / login_n)

    login_img = login_img.resize((3000,1400),Image.ANTIALIAS)
    img = ImageTk.PhotoImage(login_img)
    Canvas1 = Canvas(admin_login)
    Canvas1.create_image(300,340,image = img)      
    Canvas1.config(bg="white",width = new_img_width, height = new_img_height)
    Canvas1.pack(expand=True,fill=BOTH)

    #login as member instead
    def member_log():
        admin_login.destroy()
        user_login_page()

    #Admin authentication
    def auth_admin():
        if (admin_login_entry.get(), admin_password_login.get()) in admin:
            admin_login.destroy()
            admin_sess_view()
        else:
            messagebox.showwarning(message = ("Unauthorised Login: Admin details not recognised!")) 

    #Implementing Label
    headingFrame1 = Frame(admin_login,bg="#FFBB00",bd=5)
    headingFrame1.place(relx=0.2,rely=0.1,relwidth=0.6,relheight=0.18)
    headingLabel = Label(headingFrame1, text="Admin Login Page", bg='brown', fg='white', font=('Calibri',20))
    headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)

    #Implementing User login label
    admin_id_label = Label(admin_login, text="Enter AdminID", font=('Calibri',10, 'underline'))
    admin_id_label.place(relx=0.40,rely=0.35, relwidth=0.20,relheight=0.04)
    admin_password_label = Label(admin_login, text="Enter Password", font=('Calibri',10, 'underline'))
    admin_password_label.place(relx=0.40,rely=0.50, relwidth=0.20,relheight=0.04)


    #Text Boxes for Entry
    admin_login_entry = Entry(admin_login, width = 30)
    admin_login_entry.place(relx=0.28,rely=0.40, relwidth=0.45,relheight=0.04)
    admin_password_login = Entry(admin_login, width = 30)
    admin_password_login.place(relx=0.28,rely=0.55, relwidth=0.45,relheight=0.04)
    
    #Adding Button
    registration = Button(admin_login,text="Return to Member Login",bg='cadetblue', fg='white', command = member_log)
    registration.place(relx=0.28,rely=0.80, relwidth=0.45,relheight=0.08)
    login_button = Button(admin_login,text="Login",bg='red', fg='white', command = auth_admin)
    login_button.place(relx=0.28,rely=0.70, relwidth=0.45,relheight=0.08)

    admin_login.mainloop()

def simplesearch():
    editor.withdraw()
    global editor3

    def main_page():
        editor3.destroy()
        editor.deiconify()

    editor3 = Toplevel()
    editor3.title("Simple Search")
    editor3.minsize(width=400, height=700)
    editor3.geometry("700x700")

    bg_n, check_bg = 0.25, True

    # Background image
    login_img = Image.open("lib.jpg")
    [img_width, img_height] = login_img.size
    login_n, check_login = 0.25, True
    new_img_width = int(img_width * login_n)
    if check_login:
        new_img_height = int(img_height * login_n)
    else:
        new_img_height = int(img_height / login_n)

    login_img = login_img.resize((3000, 1400), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(login_img)
    Canvas1 = Canvas(editor3)
    Canvas1.create_image(300, 340, image=img)
    Canvas1.config(bg="white", width=new_img_width, height=new_img_height)
    Canvas1.pack(expand=True, fill=BOTH)

    # Implementing Label
    headingFrame1 = Frame(editor3, bg="#FFBB00", bd=5)
    headingFrame1.place(relx=0.2, rely=0.1, relwidth=0.6, relheight=0.18)
    headingLabel = Label(headingFrame1, text="Simple Search", bg='brown', fg='white', font=('Calibri', 20))
    headingLabel.place(relx=0, rely=0, relwidth=1, relheight=1)

    # Implementing Simple Search Function label
    simple_search_label = Label(editor3, text="Enter Title(s)", font=('Calibri', 10, 'underline'))
    simple_search_label.place(relx=0.40, rely=0.35, relwidth=0.20, relheight=0.04)

    # Global variables for login text entry
    global simple_search_input

    # Text Boxes for Entry
    simple_search_input = Entry(editor3, width=30)
    simple_search_input.place(relx=0.28, rely=0.40, relwidth=0.45, relheight=0.04)

    #Adding Buttons
    simple_search_button = Button(editor3, text="Enter", bg='cadetblue', fg='white', command=auth_simplesearch)
    simple_search_button.place(relx=0.40, rely=0.45, relwidth=0.20, relheight=0.04)
    previous = Button(editor3, text="Go back to user menu", bg='cadetblue', fg='white', command=main_page)
    previous.place(relx=0.28, rely=0.70, relwidth=0.45, relheight=0.08)

    editor3.mainloop()

def auth_simplesearch():
    global editor4
    simple_search_result = simple_search_input.get()


    # Connecting to MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    database = client["Books"]
    col = database["BT2102"]

    # Connecting to MySQL Database
    db = mysql.connect(host="localhost",
                       user="root",
                       password=mysqlpassword,
                       database="ils2",
                       autocommit=True)
    command_handler = db.cursor(buffered=True)

    bg_n, check_bg = 0.25, True

    keywords = simple_search_result.split(" ")
    checker = False
    bookids = []
    for keyword in keywords:
        x = col.find({"title": {"$regex": keyword, "$options": "i"}}, {"title": 1})
        initial_bookids_length = len(bookids)
        for i in x:
            bookids += [i['_id']]
        if len(bookids) == initial_bookids_length:
            checker = True

    result = []
    for bookid in bookids:
        command_handler.execute("SELECT T1.BookID, T1.Title, T2.UserID, T2.ExpectedDueDate FROM book T1 LEFT JOIN LoanStatus T2 ON T1.BookID=T2.BookID WHERE T1.BookID=%s", (bookid,))
        outcome = command_handler.fetchall()
        for entry in outcome:
            if entry[2]:
                result += [entry]
            else:
                command_handler.execute("SELECT T1.BookID, T1.Title, T3.UserID, T2.ExpectedDueDate FROM book T1 LEFT JOIN LoanStatus T2 ON T1.BookID=T2.BookID LEFT JOIN ReserveStatus T3 ON T1.BookID= T3.BookID WHERE T1.BookID=%s", (bookid,))
                outcome2 = command_handler.fetchall()
                for entry in outcome2:
                    result +=[entry]
                
            

    if keywords == [""] or checker == True:
        result =[]

    if not result:
        return messagebox.showwarning(message="No search results found!")
    else:
        editor4 = Toplevel()
        editor4.title("Simple Search")
        editor4.geometry("700x700")
        row_counter = 1
        #column headings
        e1 = Entry(editor4, width=30, fg="blue")
        e1.grid(row=0, column=0)
        e1.insert(END, "Book ID:")
        e2 = Entry(editor4, width=30, fg="blue")
        e2.grid(row=0, column=1)
        e2.insert(END, "Title: ")
        e3 = Entry(editor4, width=30, fg="blue")
        e3.grid(row=0, column=2)
        e3.insert(END, "Availability: ")
        e4 = Entry(editor4, width=30, fg="blue")
        e4.grid(row=0, column=3)
        e4.insert(END, "Expected Due Date: ")  
        for lib_entry in result:
            for j in range(len(lib_entry)):
                e = Entry(editor4, width=30, fg="blue")
                e.grid(row=row_counter, column=j)
                if j == 2:
                    if str(lib_entry[j]) == "None":
                        entry = "Available"
                    else:
                        entry = "Not Available"
                else:
                    entry = str(lib_entry[j])
                e.insert(END, entry)
            row_counter += 1


def advancedsearch():
    editor.withdraw()
    global advanced

    def main_page():
        advanced.destroy()
        editor.deiconify()

    advanced = Toplevel()
    advanced.title("Advanced Search")
    advanced.minsize(width=400, height=700)
    advanced.geometry("700x700")

    bg_n, check_bg = 0.25, True

    # Background image
    login_img = Image.open("lib.jpg")
    [img_width, img_height] = login_img.size
    login_n, check_login = 0.25, True
    new_img_width = int(img_width * login_n)
    if check_login:
        new_img_height = int(img_height * login_n)
    else:
        new_img_height = int(img_height / login_n)

    login_img = login_img.resize((3000, 1400), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(login_img)
    Canvas1 = Canvas(advanced)
    Canvas1.create_image(300, 340, image=img)
    Canvas1.config(bg="white", width=new_img_width, height=new_img_height)
    Canvas1.pack(expand=True, fill=BOTH)

    # Implementing Label
    headingFrame1 = Frame(advanced, bg="#FFBB00", bd=5)
    headingFrame1.place(relx=0.2, rely=0.1, relwidth=0.6, relheight=0.18)
    headingLabel = Label(headingFrame1, text="Advanced Search", bg='brown', fg='white', font=('Calibri', 20))
    headingLabel.place(relx=0, rely=0, relwidth=1, relheight=1)

    # Implementing Advanced Search Function label
    author_search_label = Label(advanced, text="Enter Author(s)", font=('Calibri', 10, 'underline'))
    author_search_label.place(relx=0.40, rely=0.35, relwidth=0.20, relheight=0.04)
    category_search_label = Label(advanced, text="Enter Categories", font=('Calibri', 10, 'underline'))
    category_search_label.place(relx=0.40, rely=0.45, relwidth=0.20, relheight=0.04)
    YOP_search_label = Label(advanced, text="Enter Year of Publication", font=('Calibri', 10, 'underline'))
    YOP_search_label.place(relx=0.35, rely=0.55, relwidth=0.30, relheight=0.04)

    # Global variables for login text entry
    global author_search_input
    global category_search_input
    global YOP_search_input

    # Text Boxes for Entry
    author_search_input = Entry(advanced, width=30)
    author_search_input.place(relx=0.28, rely=0.40, relwidth=0.45, relheight=0.04)
    category_search_input = Entry(advanced, width=30)
    category_search_input.place(relx=0.28, rely=0.50, relwidth=0.45, relheight=0.04)
    YOP_search_input = Entry(advanced, width=30)
    YOP_search_input.place(relx=0.28, rely=0.60, relwidth=0.45, relheight=0.04)

    # Adding Buttons
    advanced_search_button = Button(advanced, text="Enter", bg='cadetblue', fg='white', command=auth_advancedsearch)
    advanced_search_button.place(relx=0.40, rely=0.65, relwidth=0.20, relheight=0.04)
    previous = Button(advanced, text="Go back to user menu", bg='cadetblue', fg='white', command=main_page)
    previous.place(relx=0.28, rely=0.70, relwidth=0.45, relheight=0.08)

    advanced.mainloop()

def auth_advancedsearch():
    global editor5
    answerAuthor = author_search_input.get()
    answerCategory = category_search_input.get()
    answerYearsOfPublication = YOP_search_input.get()

    # Connecting to MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    database = client["Books"]
    col = database["BT2102"]

    # Connecting to MySQL Database
    db = mysql.connect(host="localhost",
                       user="root",
                       password=mysqlpassword,
                       database="ils2",
                       autocommit=True)
    command_handler = db.cursor(buffered=True)

    bg_n, check_bg = 0.25, True
    
    keywordsAuthor = []
    keywordsCategory = []
    keywordsYearsOfPublication = []
            
    finalAuthor = []
    finalCategory = []
    finalYearsOfPublication = []
    filledLists = []
    final = []

    keywordsAuthor = answerAuthor.split(" ")
    keywordsCategory = answerCategory.split(" ")
    keywordsYearsOfPublication = answerYearsOfPublication.split(" ")

    checker = False

    for kA in keywordsAuthor:
        x = col.find({"authors" : {"$regex": kA, "$options": "i"}}, {"title": 1, "authors": 1})
        initial_finalAuthor_length = len(finalAuthor)
        for i in x:
            finalAuthor += [i['_id']]
        if len(finalAuthor) == initial_finalAuthor_length:
            checker = True
    for kC in keywordsCategory:
        y = col.find({"categories" : {"$regex": kC, "$options": "i"}}, {"title": 1, "authors": 1})
        initial_finalCategory_length = len(finalCategory)
        for j in y:
            finalCategory += [j['_id']]
        if len(finalCategory) == initial_finalCategory_length:
            checker = True
    if keywordsYearsOfPublication!=[""]:
        for kY in keywordsYearsOfPublication:
            if len(kY) == 4:
                z = col.find({"publishedDate": {"$gte": datetime(int(kY),1,1),"$lt": datetime(int(kY),12,31)}}, {"title": 1, "authors": 1})
                initial_finalYearsOfPublication_length = len(finalYearsOfPublication)
                for k in z:
                    finalYearsOfPublication += [k['_id']]
                if len(finalYearsOfPublication) == initial_finalYearsOfPublication_length:
                    checker = True
            else:
                checker = True
                    
    def isFilled(list):
        return list != []

    if isFilled(finalAuthor):
        filledLists.append(finalAuthor)

    if isFilled(finalCategory):
        filledLists.append(finalCategory)

    if isFilled(finalYearsOfPublication):
        filledLists.append(finalYearsOfPublication)
        
    if len(filledLists) == 0:
        final = []
    elif len(filledLists) == 1:
        final = filledLists[0]
    elif len(filledLists) == 2:
        final = [entry for entry in filledLists[0] if entry in filledLists[1]]
    else:
        i = [entry for entry in filledLists[0] if entry in filledLists[1]]
        final = [entry for entry in i if entry in filledLists[2]]

    for lst in filledLists:
        if not isFilled(lst):
            final = []
    if checker == True:
        final = []
    if keywordsAuthor == [""] and keywordsCategory == [""] and keywordsYearsOfPublication == [""]:
        final = []
    
    result = []
    for entry in final:
        command_handler.execute("SELECT T1.BookID, T1.Title, T2.UserID, T2.ExpectedDueDate FROM book T1 LEFT JOIN LoanStatus T2 ON T1.BookID=T2.BookID WHERE T1.BookID=%s", (entry,))
        outcome = command_handler.fetchall()
        for element in outcome:
            if element[2]:
                result += [element]
            else:
                command_handler.execute("SELECT T1.BookID, T1.Title, T3.UserID, T2.ExpectedDueDate FROM book T1 LEFT JOIN LoanStatus T2 ON T1.BookID=T2.BookID LEFT JOIN ReserveStatus T3 ON T1.BookID= T3.BookID WHERE T1.BookID=%s", (entry,))
                outcome2 = command_handler.fetchall()
                for element in outcome2:
                    result +=[element]
                

    if not result:
        return messagebox.showwarning(message = "No search results found!")
    else:
        editor5 = Toplevel()
        editor5.title("Advanced Search")
        editor5.geometry("1000x700")
        row_counter = 1
        #column headings
        e1 = Entry(editor5, width=50, fg="blue")
        e1.grid(row=0, column=0)
        e1.insert(END, "Book ID:")
        e2 = Entry(editor5, width=50, fg="blue")
        e2.grid(row=0, column=1)
        e2.insert(END, "Title: ")
        e3 = Entry(editor5, width=50, fg="blue")
        e3.grid(row=0, column=2)
        e3.insert(END, "Availability: ")
        e4 = Entry(editor5, width=50, fg="blue")
        e4.grid(row=0, column=3)
        e4.insert(END, "Expected Due Date: ") 
        for lib_entry in result:
            for j in range(len(lib_entry)):
                e = Entry(editor5, width=50, fg="blue")
                e.grid(row=row_counter, column=j)
                if j == 2:
                    if str(lib_entry[j]) == "None":
                        entry = "Available"
                    else:
                        entry = "Not Available"
                else:
                    entry = str(lib_entry[j])
                e.insert(END, entry)
            row_counter += 1


def bookBorrow():
    global bookBorrow

    db = mysql.connect(host="localhost",
                       user="root",
                       password=mysqlpassword,
                       database="ils2",
                       autocommit=True)
    command_handler = db.cursor(buffered=True)

    command_handler.execute("SELECT * FROM LoanStatus WHERE UserID = %s", (user_login_input,))
    bookCount = len(command_handler.fetchall())

    bookID = borrow_input.get()
    # command_handler.execute("SELECT bookID FROM book WHERE Title = %s", (book,))
    # bookID = command_handler.fetchone()[0]

    command_handler.execute("SELECT FineDateTime, FineAmount FROM Fine WHERE UserID = %s", (user_login_input,))
    output = command_handler.fetchall()

    command_handler.execute("SELECT UserID FROM ReserveStatus WHERE BookID = %s", (bookID,))
    checker = command_handler.fetchall()

    command_handler.execute("SELECT COUNT(1) FROM book WHERE BookID = %s", (bookID,))
    bookID_check = command_handler.fetchone()[0]

    if bookID_check == 0:
        return messagebox.showinfo(message="Sorry, no such bookID in our library. Please check again.")
    if output:
        return messagebox.showinfo(message="Sorry, unable to borrow books as you have outstanding fines.")
    if bookCount == 4:
        return messagebox.showinfo(message="Sorry, maximum number of books(4) borrowed. Return some books to borrow more.")
    if checker:
        checker_userid = checker[0][0]
        if checker_userid != user_login_input:
            return messagebox.showinfo(message="Sorry, book has been reserved by another user.")

    command_handler.execute("SELECT COUNT(1) FROM LoanStatus WHERE BookID = %s", (bookID,))
    result = command_handler.fetchone()[0]
    if result == 1:
        return messagebox.showinfo(message="Sorry, no such book/book is currently on loan.")
    else:
        dueDate = datetime.now() + timedelta(days=28)
        formatted_date = dueDate.strftime('%Y-%m-%d %H:%M:%S')
        sql = "INSERT INTO LoanStatus (BookID, UserID, ExpectedDueDate, ExtensionStatus) VALUES (%s, %s, %s, %s)"
        val = (bookID, user_login_input, formatted_date, False)
        command_handler.execute(sql, val)
        if checker:
            if checker_userid == user_login_input:
                command_handler.execute("DELETE FROM ReserveStatus WHERE UserID = %s", (user_login_input,))
        return messagebox.showinfo(message="Book has been successfully borrowed.")

def borrow_page():
    editor.withdraw()
    global borrow

    def main_page():
        borrow.destroy()
        editor.deiconify()

    db = mysql.connect(host="localhost",
                       user="root",
                       password=mysqlpassword,
                       database="ils2",
                       autocommit=True)
    command_handler = db.cursor(buffered=True)

    borrow = Toplevel()
    borrow.title("Book Borrowing")
    borrow.minsize(width = 400, height = 700)
    borrow.geometry("700x700")

    bg_n, check_bg = 0.25, True

    #Background image
    login_img = Image.open("lib.jpg")
    [img_width, img_height] = login_img.size
    login_n, check_login = 0.25, True
    new_img_width = int(img_width * login_n)
    if check_login:
        new_img_height = int(img_height * login_n)
    else:
        new_img_height = int(img_height / login_n)

    login_img = login_img.resize((3000, 1400), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(login_img)
    Canvas1 = Canvas(borrow)
    Canvas1.create_image(300, 340, image=img)
    Canvas1.config(bg="white", width=new_img_width, height=new_img_height)
    Canvas1.pack(expand=True, fill=BOTH)

    # Implementing Label
    headingFrame1_borrow = Frame(borrow, bg="#FFBB00", bd=5)
    headingFrame1_borrow.place(relx=0.2, rely=0.1, relwidth=0.6, relheight=0.18)
    headingLabel_borrow = Label(headingFrame1_borrow, text="Borrow Books", bg='brown',fg='white', font=('Calibri', 20))
    headingLabel_borrow.place(relx=0, rely=0, relwidth=1, relheight=1)

    #Implementing Borrow Books label
    borrow_label = Label(borrow, text="Please enter the bookID of the book you would like to borrow",
                         font=('Calibri', 12, 'underline'))
    borrow_label.place(relx=0.18, rely=0.35, relwidth=0.65, relheight=0.04)

    global borrow_input

    #Text Boxes for Entry
    borrow_input = Entry(borrow, width=30)
    borrow_input.place(relx=0.28, rely=0.40, relwidth=0.45, relheight=0.04)

    #Adding button
    borrowBook = Button(borrow, text="Borrow Book", bg='red', fg='white', command=bookBorrow)
    borrowBook.place(relx=0.28, rely=0.50, relwidth=0.45, relheight=0.08)
    previous = Button(borrow, text="Go back to user menu", bg='cadetblue', fg='white', command=main_page)
    previous.place(relx=0.28, rely=0.70, relwidth=0.45, relheight=0.08)

    borrow.mainloop()

def bookReserve():
    global bookReserve

    db = mysql.connect(host="localhost",
                       user="root",
                       password=mysqlpassword,
                       database="ils2",
                       autocommit=True)
    command_handler = db.cursor(buffered=True)

    bookID = reserve_input.get()

    command_handler.execute("SELECT COUNT(1) FROM ReserveStatus WHERE BookID = %s", (bookID,))
    result = command_handler.fetchone()[0]

    command_handler.execute("SELECT COUNT(1) FROM LoanStatus WHERE BookID = %s", (bookID,))
    answer = command_handler.fetchone()[0]

    command_handler.execute("SELECT FineDateTime, FineAmount FROM Fine WHERE UserID = %s", (user_login_input,))
    fineOutput = command_handler.fetchall()

    command_handler.execute("SELECT COUNT(1) FROM book WHERE BookID = %s", (bookID,))
    book = command_handler.fetchone()[0]

    if book == 0:
        return messagebox.showinfo(message="Sorry, no such bookID in our library. Please check again.")
    if fineOutput:
        return messagebox.showinfo(message="Sorry, unable to reserve books as you have outstanding fines.")
    if result == 1:
        return messagebox.showinfo(message="Sorry, this book has already been reserved.")
    if answer == 0:
        return messagebox.showinfo(message="The book is currently available to be borrowed.")
    else:
        command_handler.execute("SELECT UserID FROM LoanStatus WHERE BookID = %s", (bookID,))
        userID = command_handler.fetchall()[0]
        if userID[0] == user_login_input:
            return messagebox.showinfo(message="Sorry, book cannot be reserved as you are currently borrowing this book.")
        else:
            reserveDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            sql = "INSERT INTO ReserveStatus (BookID, UserID, ReserveDate) VALUES (%s, %s, %s)"
            val = (bookID, user_login_input, reserveDate)
            command_handler.execute(sql, val)
            return messagebox.showinfo(message="Book has been successfully reserved")

def reserve_page():
    editor.withdraw()
    global reserve

    def main_page():
        reserve.destroy()
        editor.deiconify()

    db = mysql.connect(host="localhost",
                       user="root",
                       password=mysqlpassword,
                       database="ils2",
                       autocommit=True)
    command_handler = db.cursor(buffered=True)

    reserve = Toplevel()
    reserve.title("Book Reserving")
    reserve.minsize(width=400, height=700)
    reserve.geometry("700x700")

    bg_n, check_bg = 0.25, True

    # Background image
    login_img = Image.open("lib.jpg")
    [img_width, img_height] = login_img.size
    login_n, check_login = 0.25, True
    new_img_width = int(img_width * login_n)
    if check_login:
        new_img_height = int(img_height * login_n)
    else:
        new_img_height = int(img_height / login_n)

    login_img = login_img.resize((3000, 1400), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(login_img)
    Canvas1 = Canvas(reserve)
    Canvas1.create_image(300, 340, image=img)
    Canvas1.config(bg="white", width=new_img_width, height=new_img_height)
    Canvas1.pack(expand=True, fill=BOTH)

    # Implementing Label
    headingFrame1_reserve = Frame(reserve, bg="#FFBB00", bd=5)
    headingFrame1_reserve.place(relx=0.2, rely=0.1, relwidth=0.6, relheight=0.18)
    headingLabel_reserve = Label(headingFrame1_reserve, text="Reserve Books", bg='brown', fg='white', font=('Calibri', 20))
    headingLabel_reserve.place(relx=0, rely=0, relwidth=1, relheight=1)

    # Implementing Reserving Books label
    reserve_label = Label(reserve, text="Please enter the BookID of the book you would like to reserve", font=('Calibri', 12, 'underline'))
    reserve_label.place(relx=0.18, rely=0.35, relwidth=0.65, relheight=0.04)

    global reserve_input

    #Text Boxes for Entry
    reserve_input = Entry(reserve, width=30)
    reserve_input.place(relx=0.28, rely=0.40, relwidth=0.45, relheight=0.04)

    #Adding button
    reserveBook = Button(reserve, text="Reserve Book", bg='red', fg='white', command=bookReserve)
    reserveBook.place(relx=0.28, rely=0.50, relwidth=0.45, relheight=0.08)
    previous = Button(reserve, text="Go back to user menu", bg='cadetblue', fg='white', command=main_page)
    previous.place(relx=0.28, rely=0.70, relwidth=0.45, relheight=0.08)

    reserve.mainloop()    




#Member session
def member_sess():
    root.withdraw()
    update_fines()
    global editor

    editor = Toplevel()
    editor.title("Integrated Library Management System")
    editor.minsize(width = 400, height = 700)
    editor.geometry("700x700")

    bg_n, check_bg = 0.25, True

    #Background image
    login_img = Image.open("lib.jpg")       
    [img_width, img_height] = login_img.size
    login_n, check_login = 0.25, True
    new_img_width = int(img_width * login_n)
    if check_login:
        new_img_height = int (img_height * login_n)
    else:
        new_img_height = int (img_height / login_n)

    login_img = login_img.resize((3000,1400),Image.ANTIALIAS)
    img = ImageTk.PhotoImage(login_img)
    Canvas1 = Canvas(editor)
    Canvas1.create_image(300,340,image = img)      
    Canvas1.config(bg="white",width = new_img_width, height = new_img_height)
    Canvas1.pack(expand=True,fill=BOTH)

  

    #Implementing Label
    headingFrame1 = Frame(editor,bg="#FFBB00",bd=5)
    headingFrame1.place(relx=0.2,rely=0.1,relwidth=0.6,relheight=0.18)
    headingLabel = Label(headingFrame1, text="User Session", bg='brown', fg='white', font=('Calibri',20))
    headingLabel.place(relx=0,rely=0, relwidth=1, relheight=1)
    
    #Adding Button
    simple_search = Button(editor,text="1: Simple Search",bg='cadetblue', fg='white', command=simplesearch)
    simple_search.place(relx=0.28,rely=0.4, relwidth=0.45,relheight=0.04)
    
    advanced_search = Button(editor,text="2: Advanced Search",bg='cadetblue', fg='white', command=advancedsearch)
    advanced_search.place(relx=0.28,rely=0.45, relwidth=0.45,relheight=0.04)
    
    borrow = Button(editor,text="3: Borrow",bg='cadetblue', fg='white', command = borrow_page)
    borrow.place(relx=0.28,rely=0.50, relwidth=0.45,relheight=0.04)
    
    reserve = Button(editor,text="4: Reserve",bg='cadetblue', fg='white', command=reserve_page)
    reserve.place(relx=0.28,rely=0.55, relwidth=0.45,relheight=0.04)
    
    manage = Button(editor,text="5: Manage Books/Reservations",bg='cadetblue', fg='white', command=manage_books)
    manage.place(relx=0.28,rely=0.60, relwidth=0.45,relheight=0.04)
    
    fines = Button(editor,text="6: Fines and Payments",bg='cadetblue', fg='white', command = fines_payment)
    fines.place(relx=0.28,rely=0.65, relwidth=0.45,relheight=0.04)

    logout = Button(editor,text="7: Logout",bg='cadetblue', fg='white', command = editor_logout)
    logout.place(relx=0.28,rely=0.70, relwidth=0.45,relheight=0.04)

    editor.mainloop()

def editor_logout():
    editor.destroy()
    root.deiconify()
    

    
#Connecting to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
database = client["Books"]
col = database["BT2102"]

#Connecting to MySQL Database
db = mysql.connect(host="localhost",
                   user="root",
                   password = mysqlpassword,  
                   database="ils2",
                   autocommit = True)
command_handler = db.cursor(buffered=True)

#Login image
login_img = Image.open("lib.jpg")       #Should change background_image
[img_width, img_height] = login_img.size
login_n, check_login = 0.25, True
new_img_width = int(img_width * login_n)
if check_login:
    new_img_height = int (img_height * login_n)
else:
    new_img_height = int (img_height / login_n)

login_img = login_img.resize((3000,1400),Image.ANTIALIAS)
img = ImageTk.PhotoImage(login_img)
Canvas1 = Canvas(root)
Canvas1.create_image(300,340,image = img)      
Canvas1.config(bg="white",width = new_img_width, height = new_img_height)
Canvas1.pack(expand=True,fill=BOTH)

    
#Login Page Frame
headingFrame1_login = Frame(root,bg="#FFBB00",bd=5)
headingFrame1_login.place(relx=0.2,rely=0.1,relwidth=0.6,relheight=0.18)
headingLabel_login = Label(headingFrame1_login, text="Integrated \n Library Management System", bg='brown', fg='white', font=('Calibri',20))
headingLabel_login.place(relx=0,rely=0, relwidth=1, relheight=1)



#Login Options
user_login = Button(root,text="User Login",bg='cadetblue', fg='white', command = user_login_page)
user_login.place(relx=0.28,rely=0.4, relwidth=0.45,relheight=0.1)
   
admin_login = Button(root,text="Admin Login",bg='red', fg='white', command = admin_login_page)
admin_login.place(relx=0.28,rely=0.70, relwidth=0.45,relheight=0.1)








root.mainloop()
