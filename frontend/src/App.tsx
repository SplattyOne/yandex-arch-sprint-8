import React from 'react';
import { ReactKeycloakProvider } from '@react-keycloak/web';
import Keycloak, { KeycloakConfig } from 'keycloak-js';
import Cookies from 'js-cookie';
import { AuthClientEvent, AuthClientError, AuthClientTokens } from '@react-keycloak/core';
import ReportPage from './components/ReportPage';

const keycloakConfig: KeycloakConfig = {
  url: process.env.REACT_APP_KEYCLOAK_URL,
  realm: process.env.REACT_APP_KEYCLOAK_REALM||"",
  clientId: process.env.REACT_APP_KEYCLOAK_CLIENT_ID||""
};

const keycloak = new Keycloak(keycloakConfig);

const App: React.FC = () => {
  const onKeycloakEvent = async (event: AuthClientEvent, error?: AuthClientError) => {
    console.log('onKeycloakEvent', event, error);
  }

  const onKeycloakTokens = async (tokens: AuthClientTokens) => {
    console.log('onKeycloakTokens', tokens);
    // Для production среды необходимо поменять на { secure: true, sameSite: 'Strict' }
    if (tokens.token)
      Cookies.set('access_token', tokens.token, { secure: false, sameSite: 'Lax' });
    if (tokens.refreshToken)
      Cookies.set('refresh_token', tokens.refreshToken, { secure: false, sameSite: 'Lax' });
    if (tokens.idToken)
      Cookies.set('id_token', tokens.idToken, { secure: false, sameSite: 'Lax' });
  }

  return (
    <ReactKeycloakProvider
      authClient={keycloak}
      initOptions={{
        pkceMethod: 'S256',  // Включение PKCE
        onLoad: 'check-sso',
      }}
      onTokens={onKeycloakTokens}
      onEvent={onKeycloakEvent}
    >
      <div className="App">
        <ReportPage />
      </div>
    </ReactKeycloakProvider>
  );
};

export default App;
