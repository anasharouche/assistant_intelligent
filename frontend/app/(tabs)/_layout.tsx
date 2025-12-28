import { Tabs, useRouter } from 'expo-router';
import { useEffect, useState } from 'react';
import { View, ActivityIndicator } from 'react-native';

import CustomTabBar from '@/components/navigation/CustomTabBar';
import { tokenStorage } from '../lib/storage/token.storage';
import { getMe } from '../lib/services/auth.service';

export default function TabsLayout() {
  const router = useRouter();
  const [checkingAuth, setCheckingAuth] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      const token = tokenStorage.get();

      // ❌ Pas de token → login
      if (!token) {
        router.replace('/(auth)/login');
        return;
      }

      try {
        // 🔐 Validation backend
        await getMe();
        setCheckingAuth(false);
      } catch {
        tokenStorage.clear();
        router.replace('/(auth)/login');
      }
    };

    checkAuth();
  }, []);

  // ⏳ Écran de chargement pendant la vérification
  if (checkingAuth) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  // ✅ UI EXISTANTE INCHANGÉE
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarShowLabel: false,
        title: '',
      }}
      tabBar={(props) => <CustomTabBar {...props} />}
    >
      <Tabs.Screen name="index" />
      <Tabs.Screen name="timetable" />
      <Tabs.Screen name="chatbot" />
      <Tabs.Screen name="documents" />
      <Tabs.Screen name="settings" />
    </Tabs>
  );
}
