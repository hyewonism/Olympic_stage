# Project Report


## ■ Solution Structure
The project includes the following components.

### **□ Routes** 

Defined to manage a variety of functionalities, including admin search, event management, user login, and user registration. Specific functions are connected to these routes.

### **□ Functions** 

Associated function that handles the logic behind it. They perform tasks such as data retrieval, processing, and rendering templates.

### **□ Templates** 

Used to produce dynamic web pages and display data to users. To pass data and render the appropriate content, routes and functions work with templates.

## ■ Assumptions and Design Decisions
### **□ Assumptions**
1) The project assumes the existence of an administrative role with specific privileges and functionalities, including the admin search feature.
2) The project assumes specific criteria for the admin search functionality, which are not explicitly mentioned in the project brief.

### **□ Design Decisions**
1) Page template sharing: The decision of whether to share a page template between the public and admin sections or use separate templates was not mentioned in the project brief.
The chosen approach will depend on factors such as code organisation, reusability, and separation of concerns.
2) Method Detection: For the purpose of choosing which page to display or what action to take, the project may recognise the GET or POST method.
The requirements of the project, design factors, and security best practises will determine how and why this method detection is implemented.

## ■ Support for Multiple Olympics
If the application were to support multiple different Olympics (e.g., summer and winter), the following changes would be required.

### **□ Changed to Databese Tables**

Each Olympic event's specific data would need to be stored in its own set of tables. For the purpose of incorporating new attributes or relationships, it may be necessary to modify existing tables.

### **□ Changes to Web App Design and Implementation**

The web application's design and implementation would need to handle the selection and display of different Olympic events. This would involve modifying routes, functions, and templates to support multiple events.

### **□ Note**

The actual implementation of these changes is not included in the current version of the application.
