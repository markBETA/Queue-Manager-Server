Version 0.0.1
=============
    * Added the socket.io functionality for users (front-end) and printers.
    * Added the database manager and the defined models.
    * Added the blacklist manager to control the active tokens used for authenticate.
    * Added the api resources for both the front-end and the printers.
    * Added a full unit test suite of the server.

Version 0.0.2 (BETA version)
============================
    * Now the GCODE upload and download is managed together with Nginx at production environment.
    * Changed the route **POST /jobs** to **POST /jobs/create**.
    * Added the **PUT /jobs/<int:job_id>/reprint** for reprinting done jobs.
    * Swagger documentation revised and corrected.
    * Database module updated to v0.0.2
    * Blacklist manager module updated to v0.0.2
    * Added the 'FileDescriptor' class of the file manager.
    * Improved the file manager errors and warnings.
    * Added the Nginx support to the file manager for saving the files.
    * Improved the Socket.IO manager base class.
    * Added a customized Socket.IO namespace class.
    * Improved the Socket.IO manager class functions error detection.
    * Updated the application factory.
    * Updated the configuration files structure.
    * Improved the production environment deployment with Gunicorn.
    * Added the Domestic Data Streamers specific production config.
    * Improved the printer connection authorization mechanism.

Version 0.1.0
=============
    * Added the identity module for retrieving the identity of the users
    * Removed the blacklist module.
    * Now the server can be splitted to serve only the Socket.IO or the API namespaces.
    * Added and corrected documentation.
    * Minor error fixes.
