# YOUR PROJECT TITLE
#### Video Demo:  <URL HERE>
#### Description:
The Wedding Planner application is designed to help couples keep track of their wedding details. In this tool, various scenarios for the wedding can be planned, allowing for different plans for multiple locations, dates, or other details.

The first interaction with the tool is authentication or registration. Initially, a user must register, and the saved password is stored as an encrypted hash value along with the username in a database. After a successful login, the logged-in user can change their password, log out, select an existing project, or create a new project.

When changing the password, both the username and the old password must be entered to generate a new password. When creating a new project, the title, the name of the bride, the name of the groom, the location, and the wedding date can be entered. At a minimum, a project title and either the name of the groom or the name of the bride must be entered. This is mandatory because there must be at least one person responsible for the wedding.

When opening a project after creation or directly from the logged-in page, the initially specified parameters can be modified. Additionally, three more menu items appear: Checklist, Guest, and Budget. In each wedding folder, these three things can be planned and saved.

In the Checklist tab, a checklist can be created by listing what still needs to be done. Each checklist item is provided with a description expressing what specifically still needs to be done. Each item also has a checkbox that can be ticked for completed items. The call itself is made through a JavaScript method that registers when the click occurs and what action should be taken afterward. Additionally, an item can be completely deleted via a trash can symbol if it has become obsolete.

In the Guest tab, guests can be defined by entering their first and last names. By default, the guest is entered into the database without a response. In the displayed table, after a guest's response, they can be checked off with a checkbox or deleted via a trash can symbol. The number of guests and the number of guest responses are tracked below the table.

In the Budget tab, the user keeps track of the income and expenses of the wedding. Below the table, the user can directly see the total income and expenses. The table itself is sorted by date and allows the user to add a description for better tracking. Expenses are represented with a negative sign in the table. Additionally, transaction items can be deleted via a trash can symbol.

Through the different projects and the Checklist, Guest, and Budget tabs, the user can maintain a complete overview of the most important factors of a wedding, ensuring that nothing stands in the way of a beautiful celebration.