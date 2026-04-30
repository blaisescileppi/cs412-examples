// Login screen

import { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, Alert, KeyboardAvoidingView, Platform } from 'react-native';
import { styles } from '../../assets/my_styles';
import { useAuth } from '@/contexts/AuthContext';

const API_BASE = 'http://127.0.0.1:8000/mini_insta/api';

export default function LoginScreen() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { token, login, logout } = useAuth();

  const handleLogin = async () => {
    if (!username.trim() || !password.trim()) {
      Alert.alert('Missing info', 'Please enter both username and password.');
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();
      console.log('Login response:', data);

      if (response.ok) {
        login(data.token, data.profile_id);
        setUsername('');
        setPassword('');
      } else {
        Alert.alert('Login failed', data.error || 'Check your username and password.');
      }
    } catch (error) {
      console.log('Login error:', error);
      Alert.alert('Error', 'Could not connect to server.');
    }
  };

  if (token) {
    return (
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
        <View style={styles.loginWrapper}>
          <Text style={styles.logoIcon}>📸</Text>
          <Text style={styles.logoText}>MiniInsta</Text>

          <View style={styles.loggedInCard}>
            <Text style={styles.loggedInText}>You&apos;re logged in!</Text>
            <Text style={styles.loggedInSub}>Check out the other tabs.</Text>
          </View>

          <View style={styles.dividerRow}>
            <View style={styles.dividerLine} />
            <Text style={styles.dividerText}>OR</Text>
            <View style={styles.dividerLine} />
          </View>

          <TouchableOpacity style={styles.logoutButton} onPress={logout}>
            <Text style={styles.logoutButtonText}>Log Out</Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    );
  }

  return (
    <KeyboardAvoidingView
      style={{ flex: 1 }}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
      <View style={styles.loginWrapper}>
        <Text style={styles.logoIcon}>📸</Text>
        <Text style={styles.logoText}>MiniInsta</Text>

        <TextInput
          style={styles.inputFull}
          value={username}
          onChangeText={setUsername}
          placeholder="Username"
          autoCapitalize="none"
          autoCorrect={false}
          placeholderTextColor="#aaa"
        />

        <TextInput
          style={styles.inputFull}
          value={password}
          onChangeText={setPassword}
          placeholder="Password"
          secureTextEntry
          placeholderTextColor="#aaa"
        />

        <TouchableOpacity style={styles.loginButton} onPress={handleLogin}>
          <Text style={styles.loginButtonText}>Log In</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}
