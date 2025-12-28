import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  Image,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { useState } from 'react';

import { login } from '../lib/services/auth.service';

export default function LoginScreen() {
  const router = useRouter();

  // ===== STATE LOGIQUE (AJOUTÉ) =====
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ===== ACTION LOGIN (AJOUTÉ) =====
  const onLogin = async () => {
    if (!email || !password) {
      setError('Veuillez remplir tous les champs');
      return;
    }

    setError(null);
    setLoading(true);

    try {
      await login({ email, password });
      router.replace('/(tabs)');
    } catch (err: any) {
      // backend renvoie { error: null } ou HTTP error
      setError(
        err?.response?.data?.error?.message ||
        err?.response?.data?.detail ||
        'Email ou mot de passe incorrect'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <LinearGradient
      colors={['#5B5FEF', '#6A5AE0']}
      style={{ flex: 1 }}
    >
      <SafeAreaView style={styles.safe}>
        <View style={styles.card}>
          {/* ILLUSTRATION */}
          <Image
            source={require('../../assets/images/login.png')}
            style={styles.image}
            resizeMode="contain"
          />

          <Text style={styles.title}>Login</Text>

          {/* INPUTS */}
          <TextInput
            placeholder="Email"
            placeholderTextColor="#9CA3AF"
            style={styles.input}
            value={email}
            onChangeText={setEmail}
            autoCapitalize="none"
            keyboardType="email-address"
          />

          <TextInput
            placeholder="Password"
            placeholderTextColor="#9CA3AF"
            secureTextEntry
            style={styles.input}
            value={password}
            onChangeText={setPassword}
          />

          {/* MESSAGE ERREUR */}
          {error && (
            <Text style={{ color: 'crimson', marginBottom: 8 }}>
              {error}
            </Text>
          )}

          {/* BUTTON */}
          <TouchableOpacity
            style={styles.primaryButton}
            onPress={onLogin}
            disabled={loading}
            activeOpacity={0.85}
          >
            {loading ? (
              <ActivityIndicator color="#FFFFFF" />
            ) : (
              <Text style={styles.primaryText}>Login</Text>
            )}
          </TouchableOpacity>

          {/* FOOTER */}
          <TouchableOpacity
            onPress={() => router.push('/(auth)/register')}
          >
            <Text style={styles.link}>
              Don’t have an account? Sign Up
            </Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    </LinearGradient>
  );
}

/* ================= STYLES (INCHANGÉS) ================= */

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },

  card: {
    width: '85%',
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    padding: 24,
    alignItems: 'center',
  },

  image: {
    width: 180,
    height: 160,
    marginBottom: 12,
  },

  title: {
    fontSize: 22,
    fontWeight: '700',
    marginBottom: 20,
    color: '#111827',
  },

  input: {
    width: '100%',
    height: 48,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    paddingHorizontal: 16,
    marginBottom: 14,
    backgroundColor: '#F9FAFB',
  },

  primaryButton: {
    width: '100%',
    backgroundColor: '#5B5FEF',
    paddingVertical: 14,
    borderRadius: 14,
    alignItems: 'center',
    marginTop: 10,
  },
  primaryText: {
    color: '#FFFFFF',
    fontWeight: '600',
    fontSize: 15,
  },

  link: {
    marginTop: 16,
    color: '#5B5FEF',
    fontWeight: '600',
  },
});
