// src/pages/profile.js
import React, { useState } from 'react';

const Profile = () => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [bio, setBio] = useState('');
    
    const handleSave = () => {
        // Aquí puedes manejar la lógica para guardar los cambios en el perfil
        console.log('Perfil guardado:', { username, email, bio });
    };
    
    return (
        <div className="container">
        <h1>Perfil</h1>
        <form>
            <div className="mb-3">
            <label htmlFor="username" className="form-label">Nombre de usuario</label>
            <input
                type="text"
                className="form-control"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
            />
            </div>
            <div className="mb-3">
            <label htmlFor="email" className="form-label">Correo electrónico</label>
            <input
                type="email"
                className="form-control"
                id="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
            />
            </div>
            <div className="mb-3">
            <label htmlFor="bio" className="form-label">Biografía</label>
            <textarea
                className="form-control"
                id="bio"
                rows="3"
                value={bio}
                onChange={(e) => setBio(e.target.value)}
            ></textarea>
            </div>
            <button type="button" className="btn btn-primary" onClick={handleSave}>
            Guardar cambios
            </button>
        </form>
        </div>
    );
    }
export default Profile;