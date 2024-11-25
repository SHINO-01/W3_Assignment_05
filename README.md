
<body>

<h1>Travel API Documentation</h1>

<p>Welcome to the Travel API project! This documentation provides an overview of the microservices, their endpoints, functionalities, and instructions on how to set up, run, test, and use the application.</p>
<p>MUST USE PYTHON V3.11 or older</p>
<hr>

<h2>Table of Contents</h2>
<ul>
    <li><a href="#introduction">Introduction</a></li>
    <li><a href="#microservices-overview">Microservices Overview</a></li>
    <ul>
        <li><a href="#authentication-service">Authentication Service</a></li>
        <li><a href="#user-service">User Service</a></li>
        <li><a href="#destination-service">Destination Service</a></li>
    </ul>
    <li><a href="#setup-instructions">Setup Instructions</a></li>
    <li><a href="#running-the-project">Running the Project</a></li>
    <li><a href="#running-tests">Running Tests</a></li>
    <li><a href="#usage-guide">Usage Guide</a></li>
</ul>

<hr>

<h2 id="introduction">Introduction</h2>

<p>The Travel API is a microservices-based application designed to manage users and travel destinations. It features three main services:</p>

<ul>
    <li><strong>Authentication Service:</strong> Handles token generation and validation using JWT.</li>
    <li><strong>User Service:</strong> Manages user registration, login, and profile information.</li>
    <li><strong>Destination Service:</strong> Provides information about travel destinations and allows admins to add or delete destinations.</li>
</ul>

<hr>

<h2 id="microservices-overview">Microservices Overview</h2>

<h3 id="authentication-service">1. Authentication Service</h3>

<p>The Authentication Service is responsible for generating and validating JWT tokens for authentication purposes.</p>

<h4>Endpoints</h4>

<ul>
    <li><strong>GET /</strong>
        <ul>
            <li>Returns a welcome message.</li>
        </ul>
    </li>
    <li><strong>POST /generate_token</strong>
        <ul>
            <li>Generates a JWT token based on the provided email and role.</li>
            <li><strong>Parameters (JSON body):</strong>
                <ul>
                    <li><code>email</code> (string) - User's email address.</li>
                    <li><code>role</code> (string) - User's role (e.g., "User", "Admin").</li>
                </ul>
            </li>
        </ul>
    </li>
    <li><strong>GET /validate</strong>
        <ul>
            <li>Validates a provided JWT token and returns the payload.</li>
            <li><strong>Headers:</strong>
                <ul>
                    <li><code>Authorization</code> - Bearer token for validation.</li>
                </ul>
            </li>
        </ul>
    </li>
</ul>

<h3 id="user-service">2. User Service</h3>

<p>The User Service handles user registration, authentication, and profile management.</p>

<h4>Endpoints</h4>

<ul>
    <li><strong>GET /</strong>
        <ul>
            <li>Returns a welcome message.</li>
        </ul>
    </li>
    <li><strong>POST /register</strong>
        <ul>
            <li>Registers a new user.</li>
            <li><strong>Parameters (JSON body):</strong>
                <ul>
                    <li><code>name</code> (string) - User's full name.</li>
                    <li><code>email</code> (string) - User's email address.</li>
                    <li><code>password</code> (string) - User's password.</li>
                    <li><code>role</code> (string) - User's role ("User" or "Admin"). Only admins can create admin accounts.</li>
                </ul>
            </li>
        </ul>
    </li>
    <li><strong>POST /login</strong>
        <ul>
            <li>Authenticates a user and returns a JWT token.</li>
            <li><strong>Parameters (JSON body):</strong>
                <ul>
                    <li><code>email</code> (string) - User's email address.</li>
                    <li><code>password</code> (string) - User's password.</li>
                </ul>
            </li>
        </ul>
    </li>
    <li><strong>GET /profile</strong>
        <ul>
            <li>Retrieves the authenticated user's profile information.</li>
            <li><strong>Headers:</strong>
                <ul>
                    <li><code>Authorization</code> - Bearer token for authentication.</li>
                </ul>
            </li>
        </ul>
    </li>
</ul>

<h3 id="destination-service">3. Destination Service</h3>

<p>The Destination Service provides information about travel destinations. Admins can add or delete destinations.</p>

<h4>Endpoints</h4>

<ul>
    <li><strong>GET /</strong>
        <ul>
            <li>Returns a welcome message.</li>
        </ul>
    </li>
    <li><strong>GET /destinations</strong>
        <ul>
            <li>Retrieves a list of all destinations.</li>
            <li>User roles:
                <ul>
                    <li><strong>User:</strong> Can view destinations without the <code>id</code> field.</li>
                    <li><strong>Admin:</strong> Can view destinations with the <code>id</code> field.</li>
                </ul>
            </li>
            <li><strong>Headers:</strong>
                <ul>
                    <li><code>Authorization</code> - Bearer token for authentication (optional).</li>
                </ul>
            </li>
        </ul>
    </li>
    <li><strong>POST /destinations</strong>
        <ul>
            <li>Adds a new destination (Admin only).</li>
            <li><strong>Headers:</strong>
                <ul>
                    <li><code>Authorization</code> - Bearer token for authentication.</li>
                </ul>
            </li>
            <li><strong>Parameters (JSON body):</strong>
                <ul>
                    <li><code>id</code> (string) - Unique destination ID.</li>
                    <li><code>name</code> (string) - Destination name.</li>
                    <li><code>description</code> (string) - Destination description.</li>
                    <li><code>location</code> (string) - Destination location.</li>
                    <li><code>price_per_night</code> (number) - Price per night.</li>
                </ul>
            </li>
        </ul>
    </li>
    <li><strong>DELETE /destinations/&lt;destination_id&gt;</strong>
        <ul>
            <li>Deletes a destination by ID (Admin only).</li>
            <li><strong>Headers:</strong>
                <ul>
                    <li><code>Authorization</code> - Bearer token for authentication.</li>
                </ul>
            </li>
            <li><strong>Parameters:</strong>
                <ul>
                    <li><code>destination_id</code> (string) - ID of the destination to delete.</li>
                </ul>
            </li>
        </ul>
    </li>
</ul>

<hr>

<h2 id="setup-instructions">Setup Instructions</h2>

<h3>Prerequisites</h3>

<ul>
    <li>Python 3..11 or lower installed on your system.</li>
    <li>Git (optional, for cloning the repository).</li>
</ul>

<h3>Clone the Repository</h3>

<pre><code>git clone https://github.com/SHINO-01/W3_Assignment_05.git
cd travel-api
</code></pre>

<h3>Create a Virtual Environment</h3>

<pre><code>python -m venv venv
</code></pre>

<h3>Activate the Virtual Environment</h3>

<p>For Windows:</p>

<pre><code>venv\Scripts\activate
</code></pre>

<p>For macOS/Linux:</p>

<pre><code>source venv/bin/activate
</code></pre>

<h3>Install Dependencies</h3>

<pre><code>pip install -r requirements.txt
</code></pre>

<hr>

<h2 id="running-the-project">Running the Project</h2>

<p>The application consists of three separate services. Each service needs to be run in its own terminal window or process.</p>

<h3>Start the App</h3>

<pre><code>
python travel_api.py
</code></pre>

<p>This will start the Authentication Service on <code>http://localhost:5001</code>, User Service on <code>http://localhost:5000</code>, and the the Destination Service on <code>http://localhost:5002</code>.</p>
<p>use /apidocs after the <code>https://localhost:5000/apidocs</code> to access the flasgger UI for easy Testing and Visualization. eg. <code>http://localhost:5000/apidocs</code></p>

<hr>

<h2 id="running-tests">Running Tests</h2>

<p>The project includes a comprehensive test suite using <code>pytest</code>. Tests cover various functionalities across all services.</p>

<h3>Run All Tests</h3>

<pre><code>pytest --cov=.
</code></pre>

<p>This command runs all tests and generates a coverage report.</p>

<h3>Interpreting the Coverage Report</h3>

<p>After running the tests, you will see a coverage summary indicating the percentage of code covered by tests. The goal is to maintain at least 80% code coverage.</p>

<hr>

<h2 id="usage-guide">Usage Guide</h2>

<h3>1. Login to the Admin Account</h3>

<p>Login as Admin to use Admin Only functions.</p>

<pre><code>
Content-Type: application/json

{
    "name": "Master Admin",
    "email": "masteradmin@example.com",
    "password": "Master@123",
    "role": "Admin"
}
</code></pre>

<p><strong>Note:</strong> To create an admin account, you must be logged in as an admin.</p>

<h3>2. Register a User</h3>

<p>Send a POST request to the User Service to register a new user.</p>

<pre><code>POST http://localhost:5000/register
Content-Type: application/json

{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123",
    "role": "User"
}
</code></pre>

<p><strong>Note:</strong> To create an admin account, you must be logged in as an admin.</p>

<h3>3. Login a User</h3>

<p>Authenticate the user and receive a JWT token.</p>

<pre><code>POST http://localhost:5000/login
Content-Type: application/json

{
    "email": "john@example.com",
    "password": "password123"
}
</code></pre>

<p>The response will include an <code>access_token</code> which you will use in subsequent requests.</p>

<h3>4. Access User Profile</h3>

<p>Retrieve the authenticated user's profile information.</p>

<pre><code>GET http://localhost:5000/profile
Authorization: Bearer &lt;access_token&gt;
</code></pre>

<h3>5. View Destinations</h3>

<p>Get a list of all destinations.</p>

<pre><code>GET http://localhost:5002/destinations
Authorization: Bearer &lt;access_token&gt; (optional)
</code></pre>

<p>If you provide a valid token, you will see destinations according to your role. Admins see all fields, while users do not see the <code>id</code> field.</p>

<h3>6. Add a Destination (Admin Only)</h3>

<p>Add a new destination to the service.</p>

<pre><code>POST http://localhost:5002/destinations
Authorization: Bearer &lt;admin_access_token&gt;
Content-Type: application/json

{
    "id": "SWZ",
    "name": "Mountain Retreat",
    "description": "A serene mountain retreat.",
    "location": "Switzerland",
    "price_per_night": 200
}
</code></pre>

<h3>7. Delete a Destination (Admin Only)</h3>

<p>Delete a destination by its ID.</p>

<pre><code>DELETE http://localhost:5002/destinations/SWZ
Authorization: Bearer &lt;admin_access_token&gt;
</code></pre>

<hr>

<h2>Troubleshooting</h2>

<ul>
    <li>Ensure all services are running before making requests.</li>
    <li>Use the correct ports for each service:
        <ul>
            <li>User Service: <code>http://localhost:5000</code></li>
            <li>Authentication Service: <code>http://localhost:5001</code></li>
            <li>Destination Service: <code>http://localhost:5002</code></li>
        </ul>
    </li>
    <li>If you encounter issues with tokens, make sure to login again to get a fresh token.</li>
    <li>Check the logs in the terminal for error messages.</li>
</ul>

<hr>

<h2>Contributing</h2>

<p>Contributions are welcome! Please fork the repository and submit a pull request with your changes.</p>

<hr>

<h2>License</h2>

<p>This project is licensed under the MIT License.</p>

</body>
