a chatcode

🖥️ Advanced Dev Suite 2026
Une suite de développement moderne et sécurisée construite avec CustomTkinter. Ce projet combine un éditeur de code avec coloration syntaxique haute performance, un module de reconnaissance vocale pour le codage mains libres et une intégration de flux vidéo en direct.

🚀 Fonctionnalités
📝 Éditeur de Code Intelligent
Coloration Syntaxique : Support pour plus de 25 langages (Python, JS, C++, Rust, SQL, etc.).

Auto-détection : Identifie automatiquement le langage en fonction du contenu ou de l'extension.

Optimisation : Moteur de rendu asynchrone (debounce) pour éviter les lags lors de la frappe sur de gros fichiers.

🎙️ Module Vocal (Vocal-to-Code)
Transcription en temps réel : Utilise l'API Google Speech Recognition.

Feedback Visuel : Interface pulsante animée indiquant l'état du microphone (écoute, traitement, erreur).

Historique : Conserve une trace des commandes vocales dans un panneau dédié.

📷 Vision & Caméra
Flux Intégré : Visualisation directe de la webcam dans l'interface latérale via OpenCV.

Capture d'écran : Prise de photos instantanée enregistrée localement avec horodatage automatique.

🔐 Sécurité & Sessions
Authentification : Système de login avec hachage SHA-256 des mots de passe.

Gestion de Session : Persistance de l'utilisateur via fichiers JSON.

Historique de Connexion : Suivi des 5 dernières connexions par utilisateur.

🛠️ Installation
1. Cloner le projet
Bash
git clone https://github.com/votre-username/dev-suite-2026.git
cd dev-suite-2026
2. Dépendances
Le projet nécessite Python 3.8+ et les bibliothèques suivantes :

Bash
# Interface graphique
pip install customtkinter

# Traitement d'image et Caméra
pip install opencv-python pillow

# Reconnaissance Vocale
pip install SpeechRecognition pyaudio
Note : Pour pyaudio sur Windows, si l'installation classique échoue, utilisez pip install pipwin suivi de pipwin install pyaudio.

🏗️ Structure du Code
SyntaxHighlighter : Moteur de Regex pour la coloration des mots-clés, chaînes, et opérateurs.

CameraPanel : Gestionnaire de thread pour le flux OpenCV et la conversion PIL vers Tkinter.

VoicePanel & _VoiceRecorder : Gestion de l'écoute continue en arrière-plan via threading.

users.json : Base de données locale sécurisée pour les profils utilisateurs.

🎨 Thème Visuel
L'application utilise une palette Dark Mode inspirée de VS Code :

Arrière-plan : #1e1e1e

Panneaux : #2b2b2b

Accentuation : Thème dark-blue de CustomTkinter.

⚠️ Notes de développement
Limites de l'API Vocale : La reconnaissance vocale nécessite une connexion internet active pour l'API Google.

Performance : Le rafraîchissement de la caméra est bridé à 30ms pour préserver les ressources CPU lors de l'édition de code.

Développé avec ❤️ pour la génération 2026.

