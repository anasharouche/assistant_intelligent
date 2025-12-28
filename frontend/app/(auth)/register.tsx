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

import { register } from '../lib/services/auth.service';

export default function RegisterScreen() {
  const router = useRouter();

  // ===== STATE LOGIQUE (AJOUTÉ) =====
  const [name, setName] = useState(''); // UI seulement
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 🔐 Rôle FIXE conforme backend
  const role = 'STUDENT';

  const onRegister = async () => {
    if (!email || !password) {
      setError('Veuillez remplir tous les champs obligatoires');
      return;
    }

    setError(null);
    setLoading(true);

    try {
      await register({ email, password, role });
      router.replace('/(tabs)');
    } catch (err: any) {
      setError(
        err?.response?.data?.error?.message ||
        err?.response?.data?.detail ||
        'Inscription échouée'
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

          <Text style={styles.title}>Sign Up</Text>

          {/* INPUTS */}
          <TextInput
            placeholder="Name"
            placeholderTextColor="#9CA3AF"
            style={styles.input}
            value={name}
            onChangeText={setName}
          />

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

          {/* ERREUR */}
          {error && (
            <Text style={{ color: 'crimson', marginBottom: 8 }}>
              {error}
            </Text>
          )}

          {/* BUTTON */}
          <TouchableOpacity
            style={styles.primaryButton}
            onPress={onRegister}
            disabled={loading}
            activeOpacity={0.85}
          >
            {loading ? (
              <ActivityIndicator color="#FFFFFF" />
            ) : (
              <Text style={styles.primaryText}>Sign Up</Text>
            )}
          </TouchableOpacity>

          {/* FOOTER */}
          <TouchableOpacity
            onPress={() => router.replace('/(auth)/login')}
          >
            <Text style={styles.link}>
              Already have an account? Login
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
