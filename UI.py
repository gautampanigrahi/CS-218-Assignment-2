import os
import json
import html

COGNITO_DOMAIN = os.environ["COGNITO_DOMAIN"]
CLIENT_ID = os.environ["CLIENT_ID"]
API_BASE_URL = os.environ["API_BASE_URL"]

def lambda_handler(event, context):
    page = r"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Employee Lookup</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 700px;
            margin: 50px auto;
            padding: 20px;
        }

        input {
            padding: 10px;
            width: 250px;
            margin-right: 8px;
        }

        button {
            padding: 10px 16px;
            margin: 5px;
            cursor: pointer;
        }

        #status {
            margin: 15px 0;
            color: #333;
        }

        #result {
            margin-top: 20px;
            padding: 15px;
            background: #f1f1f1;
            white-space: pre-wrap;
        }

        .error {
            color: red;
        }
    </style>
</head>

<body>
    <h1>Employee Lookup</h1>

    <button onclick="login()">Login with Cognito</button>
    <button onclick="logout()">Logout</button>

    <p id="status">You are not logged in.</p>

    <hr>

    <input id="employeeId" placeholder="Enter Employee ID">
    <button onclick="searchEmployee()">Search</button>

    <div id="result"></div>

<script>
const cognitoDomain = "__COGNITO_DOMAIN__";
const clientId = "__CLIENT_ID__";
const apiBaseUrl = "__API_BASE_URL__";

const redirectUri = window.location.origin + window.location.pathname;

function randomString(length) {
    const characters =
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~";

    let result = "";

    const randomValues = new Uint8Array(length);
    window.crypto.getRandomValues(randomValues);

    for (let i = 0; i < length; i++) {
        result += characters[randomValues[i] % characters.length];
    }

    return result;
}

async function createCodeChallenge(verifier) {
    const data = new TextEncoder().encode(verifier);

    const digest = await window.crypto.subtle.digest("SHA-256", data);

    return btoa(String.fromCharCode(...new Uint8Array(digest)))
        .replace(/\+/g, "-")
        .replace(/\//g, "_")
        .replace(/=+$/, "");
}

async function login() {
    const verifier = randomString(64);
    const challenge = await createCodeChallenge(verifier);

    sessionStorage.setItem("code_verifier", verifier);

    const loginUrl =
        "https://" + cognitoDomain + "/oauth2/authorize" +
        "?response_type=code" +
        "&client_id=" + encodeURIComponent(clientId) +
        "&redirect_uri=" + encodeURIComponent(redirectUri) +
        "&scope=openid+email" +
        "&code_challenge=" + encodeURIComponent(challenge) +
        "&code_challenge_method=S256";

    window.location.href = loginUrl;
}

async function exchangeCodeForToken(code) {
    const verifier = sessionStorage.getItem("code_verifier");

    if (!verifier) {
        throw new Error("PKCE verifier was not found.");
    }

    const response = await fetch(
        "https://" + cognitoDomain + "/oauth2/token",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({
                grant_type: "authorization_code",
                client_id: clientId,
                code: code,
                redirect_uri: redirectUri,
                code_verifier: verifier
            })
        }
    );

    const tokens = await response.json();

    if (!response.ok) {
        throw new Error(tokens.error_description || "Token exchange failed.");
    }

    sessionStorage.setItem("id_token", tokens.id_token);
    sessionStorage.removeItem("code_verifier");

    window.history.replaceState({}, document.title, redirectUri);

    document.getElementById("status").innerText =
        "Logged in successfully.";
}

async function searchEmployee() {
    const token = sessionStorage.getItem("id_token");
    const employeeId = document.getElementById("employeeId").value.trim();
    const result = document.getElementById("result");

    if (!token) {
        result.innerHTML =
            '<p class="error">Please log in before searching.</p>';
        return;
    }

    if (!employeeId) {
        result.innerHTML =
            '<p class="error">Please enter an Employee ID.</p>';
        return;
    }

    const response = await fetch(
        apiBaseUrl + "employee/" + encodeURIComponent(employeeId),
        {
            method: "GET",
            headers: {
                "Authorization": "Bearer " + token
            }
        }
    );

    const data = await response.json();

    if (response.ok) {
        result.innerText =
            "Employee ID: " + data.employeeId + "\n" +
            "Name: " + data.name + "\n" +
            "Salary: " + data.salary + "\n" +
            "Date of Join: " + data.dateOfJoin + "\n" +
            "Description: " + data.description;
    } else if (response.status === 404) {
        result.innerHTML =
            '<p class="error">Employee not found.</p>';
    } else if (response.status === 401 || response.status === 403) {
        result.innerHTML =
            '<p class="error">Your login is missing or expired.</p>';
    } else {
        result.innerHTML =
            '<p class="error">An error occurred.</p>';
    }
}

function logout() {
    sessionStorage.removeItem("id_token");
    sessionStorage.removeItem("code_verifier");

    const logoutUrl =
        "https://" + cognitoDomain + "/logout" +
        "?client_id=" + encodeURIComponent(clientId) +
        "&logout_uri=" + encodeURIComponent(redirectUri);

    window.location.href = logoutUrl;
}

async function initializePage() {
    const params = new URLSearchParams(window.location.search);
    const code = params.get("code");

    if (code) {
        try {
            document.getElementById("status").innerText =
                "Completing login...";

            await exchangeCodeForToken(code);
        } catch (error) {
            document.getElementById("status").innerText =
                "Login failed: " + error.message;
        }

        return;
    }

    if (sessionStorage.getItem("id_token")) {
        document.getElementById("status").innerText =
            "You are logged in.";
    }
}

initializePage();
</script>

</body>
</html>
"""

    page = page.replace("__COGNITO_DOMAIN__", COGNITO_DOMAIN)
    page = page.replace("__CLIENT_ID__", CLIENT_ID)
    page = page.replace("__API_BASE_URL__", API_BASE_URL)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/html",
            "Cache-Control": "no-cache"
        },
        "body": page
    }
