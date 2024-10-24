import mysql.connector as mysql
import datetime
from datetime import datetime, timedelta
import math

mycon = mysql.connect(host='localhost', user='root', passwd='sl@user02', database='libraryms')
cur = mycon.cursor()
if mycon.is_connected():
    print("\n\n\t\t\tWelcome to Digital Library!\n\n")


def Members():
    query = "select * from members"
    cur.execute(query)
    data = cur.fetchall()
    for i in data:
        print(i)


def Issue(m, b, d):
    x = "select count(*) from transaction"
    cur.execute(x)
    data = cur.fetchone()
    total = data[0]
    t_id1 = 50100 + total + 1
    d_date = Due(d)
    query = "insert into transaction(T_ID, Book_ID, Member_ID, Issued_Date, Due_date) values({}, {}, {}, '{}', '{}')".format(t_id1, b, m, d, d_date)
    cur.execute(query)
    mycon.commit()
    print("Added Successfully!")


def Due(d):
    date_object = datetime.strptime(d, "%Y-%m-%d")
    g = timedelta(days=15)
    dd = date_object + g
    return dd.date()


def ReturnB(r, t):
    query = "select Due_Date from transaction where T_ID = {}".format(t)
    cur.execute(query)
    data = cur.fetchone()
    dd = data[0]
    x = "update transaction set Return_Date = '{}' where T_ID = {}".format(r, t)
    cur.execute(x)
    mycon.commit()
    r1 = datetime.strptime(r, "%Y-%m-%d").date()
    if r1 > dd:
        f = FineCalc(r1, dd)
        q = "update transaction set Fine = {} where T_ID = {}".format(f, t)
        cur.execute(q)
        print("Please confirm: Has the user paid the fine?")
        ans = input("Enter y/n: ")
        dom = 0
        if ans == 'y':
            dom = "update transaction set Status = '{}' where T_ID = {}".format("Paid", t)
        elif ans == 'n':
            dom = "update transaction set Status = '{}' where T_ID = {}".format("Unpaid", t)
        else:
            print("Invalid input")
            dom = 0
        if dom != 0:
            cur.execute(dom)
            mycon.commit()
    else:
        dom = "update transaction set Status = '{}' where T_ID = {}".format("Returned", t)
        cur.execute(dom)
        mycon.commit()
    print("Changes have been made.")


def FineCalc(r1, dd):
    diff = (r1 - dd).days
    fine = diff * 10
    return fine


def Search(bn):
    query = "select Title from books"
    cur.execute(query)
    data = cur.fetchall()
    t = 0
    for i in data:
        if bn in i:
            print("The book is available in this Library.")
            z = "select Title, Author, Genre, Shelf from Books where Title = '{}'".format(bn)
            cur.execute(z)
            d = cur.fetchone()
            print("Book Title:", d[0])
            print("Author:", d[1])
            print("Genre:", d[2])
            print("Found in shelf number", d[3])
            t = 1
            break
    if t == 0:
        print("The book is not available in this Library.")


def Member_His(mn, md):
    x = "select distinct Member_ID from transaction"
    cur.execute(x)
    d = cur.fetchall()
    k = 0
    for rec in d:
        if md in rec:
            k = 1
            break
    if k == 1:
        query = "select Book_ID from transaction where Member_ID = {}".format(md)
        cur.execute(query)
        data = cur.fetchall()
        print(f"\nMember {mn} has borrowed the following list of books so far\n")
        for i in data:
            bd = i[0]
            y = "select Title from books where Book_ID = {}".format(bd)
            cur.execute(y)
            p = cur.fetchone()
            print(f"Book ID: {bd}\t\tBook Title: {p[0]}\n")
    else:
        print("\nThe member has not borrowed any books yet.")


def Book_his(bn, bid):
    query = "select distinct(Book_ID) from transaction"
    cur.execute(query)
    data = cur.fetchall()
    k = 0
    for rec in data:
        if bid in rec:
            k = 1
            break
    if k == 1:
        x = "select transaction.Book_ID, books.Title, count(transaction.Book_ID ) from transaction, Books where transaction.Book_ID = Books.Book_ID and Title = '{}' group by Book_ID".format(
            bn)
        cur.execute(x)
        d = cur.fetchone()
        print(f"\nThe book {d[1]} was borrowed {d[2]} times\n")
        y = "select transaction.T_ID, transaction.Member_ID, members.Name from transaction, members where transaction.Member_ID = members.Member_ID and Book_ID = {}".format(
            bid)
        cur.execute(y)
        rs = cur.fetchall()
        print("\t\tMembers who borrowed the particular book are\n")
        for rec in rs:
            print(f"Member ID: {rec[1]} \t\t Member Name: {rec[2]}\n")
    else:
        print("\nThe particular book has not been borrowed yet.\n")


def Overdue():
    query = "select books.Book_ID, books.Title, members.Member_ID, members.Name, transaction.Due_Date from books, members, transaction where books.Book_ID = transaction.Book_ID \
            and members.Member_ID = transaction.Member_ID and Fine IS NOT NULL and Status = '{}'".format("Unpaid")
    cur.execute(query)
    data = cur.fetchall()
    t = 0
    for rec in data:
        rd = rec[4]
        date_now = datetime.today().date()
        diff = date_now - rd
        days = int(math.fabs(diff.days))
        print(f"\nMember ID: {rec[2]},\t\tMember Name: {rec[3]}\nBook Title: {rec[1]},\t\tBook ID: {rec[0]}\nDue Date: {rec[4]},\tDays since Due date: {days}\n\n")
        t = 1
    if t == 0:
        print("No Books are Overdue")


print("\t\t\tMENU\n")
print("Press 1 to view the details of our Members")
print("Press 2 to Issue a book")
print("Press 3 to Return a book")
print("Press 4 to Search a book")
print("Press 5 to View a Member's lend history")
print("Press 6 to View a Book's lend history")
print("Press 7 to View the list of Overdue Books")
choice = int(input("\nEnter your option: "))
if choice == 1:
    print("\n\t\t\tMEMBERS\n")
    Members()
elif choice == 2:
    m_id = int(input("Enter ID of the Member: "))
    b_id = int(input("Enter ID of the Book: "))
    date = input("Enter date: ")
    if int(date[5:7]) < 13 and int(date[8:]) < 32:
        Issue(m_id, b_id, date)
    else:
        print("Invalid Date")
elif choice == 3:
    t_id = int(input("Enter ID of the Transaction: "))
    r_date = input("Enter Return date: ")
    if int(r_date[5:7]) < 13 and int(r_date[8:]) < 32:
        ReturnB(r_date, t_id)
    else:
        print("Invalid Date")
elif choice == 4:
    book_name = input("Enter name of the book: ")
    Search(book_name)
elif choice == 5:
    member_name = input("Enter the Member's Name: ")
    member_id = int(input("Enter ID of the Member: "))
    Member_His(member_name, member_id)
elif choice == 6:
    book_name = input("Enter the Title of the Book: ")
    b_id = int(input("Enter ID of the Book: "))
    Book_his(book_name, b_id)
elif choice == 7:
    Overdue()
else:
    print("Invalid choice")

cur.close()
mycon.close()
