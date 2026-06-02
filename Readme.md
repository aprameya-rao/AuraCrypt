\`\`\`markdown

\# ðŸ” AuraCrypt

\> \*\*A Zero-Knowledge Multi-Modal Biometric Cryptosystem\*\*

\## ðŸ“– Project Overview

AuraCrypt is an enterprise-grade biometric authentication system that fuses physical kinetic and audio traits into a unified, zero-knowledge cryptographic lock. By implementing a \*\*Fuzzy Commitment Scheme\*\*, the system securely encrypts user identities without ever retaining sensitive raw biometric data or plaintext passwords on the server.

Instead of traditional machine learning confidence scores, this architecture utilizes strict \*\*Galois Field Mathematics (GF 2^14)\*\* and a custom \*\*Bose-Chaudhuri-Hocquenghem (BCH) error-correction engine\*\*. It deterministically authenticates users by mathematically repairing up to 330 bits (~7.1%) of natural biological noise on the fly, seamlessly bridging analog human biology with rigid cryptographic hashing.

\### âœ¨ Key Features

\* \*\*Multi-Modal Fusion:\*\* Combines 3D kinetic hand-tracking (MediaPipe) and audio MFCC vocal analysis (Librosa) into a single 4,603-bit Master Biometric Key.

\* \*\*Zero-Knowledge Storage:\*\* Uses an XOR-based Fuzzy Commitment Scheme. The database only stores "Locked Data" (absolute static), making it mathematically impossible to reverse-engineer the biometrics or the password.

\* \*\*Deterministic Error Correction:\*\* A custom Berlekamp-Massey Algorithm and Chien Search engine capable of instantly absorbing dynamic biological variance.

\* \*\*ARX Hashing:\*\* Implements a custom "TitanHash" algorithm utilizing Add-Rotate-XOR operations to create a perfect 256-bit deterministic representation of the user's password.

\---

\## ðŸ“‚ Project Structure

\`\`\`text

AuraCrypt/

â”œâ”€â”€ backend/ # FastAPI Python Backend

â”‚ â”œâ”€â”€ app/

â”‚ â”‚ â”œâ”€â”€ api/

â”‚ â”‚ â”‚ â””â”€â”€ routes.py # FastAPI routing definitions

â”‚ â”‚ â”œâ”€â”€ controllers/

â”‚ â”‚ â”‚ â””â”€â”€ biometric\_controller.py # Orchestrates the Enrollment and Login XOR logic

â”‚ â”‚ â”œâ”€â”€ services/

â”‚ â”‚ â”‚ â”œâ”€â”€ audio\_processor.py # Librosa audio extraction and binarization

â”‚ â”‚ â”‚ â”œâ”€â”€ video\_processor.py # MediaPipe kinetic tracking and temporal normalization

â”‚ â”‚ â”‚ â”œâ”€â”€ bch\_galois\_field.py # The GF(2^14) mathematical engine and log/exp tables

â”‚ â”‚ â”‚ â”œâ”€â”€ bch\_encoder.py # LFSR binary polynomial division

â”‚ â”‚ â”‚ â”œâ”€â”€ bch\_decoder.py # Syndrome Check, BMA, and Chien Search

â”‚ â”‚ â”‚ â”œâ”€â”€ crypto\_service.py # Biometric padding and ARX TitanHash

â”‚ â”‚ â”‚ â”œâ”€â”€ crypto\_constants.py # Centralized immutable cryptographic parameters

â”‚ â”‚ â”‚ â””â”€â”€ compute\_generator.py # Offline forge script for generating the BCH polynomial

â”‚ â”‚ â””â”€â”€ main.py # FastAPI application entry point

â”‚ â”œâ”€â”€ requirements.txt

â”‚ â””â”€â”€ venv/

â”œâ”€â”€ frontend/ # React Web Client

â”‚ â”œâ”€â”€ src/

â”‚ â”‚ â”œâ”€â”€ components/ # UI Components (Upload forms, webcam/mic capture)

â”‚ â”‚ â”œâ”€â”€ App.jsx

â”‚ â”‚ â””â”€â”€ main.jsx

â”‚ â”œâ”€â”€ public/

â”‚ â”œâ”€â”€ package.json

â”‚ â””â”€â”€ vite.config.js / tailwind.config.js

â””â”€â”€ README.md

\`\`\`

\## ðŸš€ How to Run the Project

\### 1. Prerequisites

\* \*\*Python 3.10+\*\* (Tested on Python 3.12)

\* \*\*Node.js 18+ & npm/yarn\*\* (For the React frontend)

\* \*\*FFmpeg\*\* installed on your system (required by Librosa/OpenCV for audio and video decoding).

\* \*Ubuntu/Debian:\* sudo apt install ffmpeg

\* \*MacOS:\* brew install ffmpeg

\### 2. Backend Installation (FastAPI)

Open a terminal and set up your Python environment:

\`\`\`bash

\# Clone the repo and enter the backend directory

git clone \[https://github.com/yourusername/AuraCrypt.git\](https://github.com/yourusername/AuraCrypt.git)

cd AuraCrypt/backend

\# Create and activate a virtual environment

python -m venv venv

source venv/bin/activate # On Windows use: venv\\Scripts\\activate

\# Install the required dependencies

pip install -r requirements.txt

\`\`\`

\### 3. Frontend Installation (React)

Open a \*\*second terminal window\*\* and set up the React environment:

\`\`\`bash

\# Navigate to the frontend directory

cd AuraCrypt/frontend

\# Install Node dependencies

npm install

\`\`\`

\### 4. Running the Application

To run the full stack, you will need to start both servers in their respective terminals.

\*\*Terminal 1 (Backend):\*\*

\`\`\`bash

cd backend

source venv/bin/activate

uvicorn app.main:app --reload

\`\`\`

\*The backend API and Swagger UI will run on http://127.0.0.1:8000\*

\*\*Terminal 2 (Frontend):\*\*

\`\`\`bash

cd frontend

npm run dev # Or 'npm start' depending on your React setup (Vite vs CRA)

\`\`\`

\*The React client will spin up and run on http://localhost:5173 (or 3000).\*

\## ðŸ› ï¸ Cryptographic Forging (Optional)

The system relies on a hardcoded 4,347-degree Generator Polynomial. If you wish to recalculate this polynomial or change the error tolerance (currently set to t=330), navigate to the backend folder and run the offline forge script:

\`\`\`bash

python app/services/compute\_generator.py

\`\`\`

\*Note: This will generate a text file containing the new array. Update app/services/crypto\_constants.py with the new values if you alter the limits.\*

\## âš ï¸ Important Note on Media Files

For testing, it is highly recommended to use \*\*Constant Framerate (CFR) .mp4\*\* files. Highly compressed Variable Framerate (VFR) files (like standard browser-recorded .webm files) can cause unpredictable frame-drops during OpenCV demuxing, which generates artificial biological noise that can exceed the 330-bit mathematical correction limit.

\`\`\`

\`\`\`