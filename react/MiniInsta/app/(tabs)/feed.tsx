// Feed screen - posts from people you follow

import { useEffect, useState } from 'react';
import { View, Text, Image, ScrollView, TouchableOpacity } from 'react-native';
import { styles } from '../../assets/my_styles';
import { useAuth } from '@/contexts/AuthContext';

const API_BASE = 'http://127.0.0.1:8000/mini_insta/api';

export default function FeedScreen() {
  const { token, profileId } = useAuth();
  const [posts, setPosts] = useState<any[]>([]);

  const loadFeed = async () => {
    if (!token || !profileId) return;
    try {
      const res = await fetch(`${API_BASE}/profiles/${profileId}/feed/`, {
        headers: { 'Authorization': `Token ${token}` },
      });
      const data = await res.json();
      setPosts(data);
      console.log('Feed loaded:', data.length, 'posts');
    } catch (e) {
      console.log('Error loading feed:', e);
    }
  };

  useEffect(() => {
    if (token && profileId) {
      loadFeed();
    }
  }, [token, profileId]);

  if (!token) {
    return (
      <View style={styles.notLoggedIn}>
        <Text style={{ fontSize: 40 }}>🔒</Text>
        <Text style={styles.notLoggedInText}>Log in to see your feed.</Text>
      </View>
    );
  }

  return (
    <ScrollView style={{ backgroundColor: '#fafafa' }}>

      {posts.length === 0 && (
        <View style={{ padding: 40, alignItems: 'center' }}>
          <Text style={{ fontSize: 36 }}>👋</Text>
          <Text style={{ color: '#8e8e8e', marginTop: 8, fontSize: 14, textAlign: 'center' }}>
            Nothing in your feed yet.{'\n'}Follow some people to see posts here.
          </Text>
        </View>
      )}

      {posts.map((post) => (
        <View key={post.id} style={styles.postCard}>

          {/* Post header: avatar + username */}
          <View style={styles.postCardHeader}>
            <View style={styles.avatarSmall} />
            <Text style={styles.postUsername}>@{post.profile_username}</Text>
          </View>

          {/* Image(s) */}
          {post.photos && post.photos.map((photo: any) =>
            photo.image ? (
              <Image key={photo.id} source={{ uri: photo.image }} style={styles.postImage} />
            ) : null
          )}

          {/* Footer: likes + caption + timestamp */}
          <View style={styles.postFooter}>
            {post.num_likes > 0 && (
              <Text style={styles.likesText}>{post.num_likes} likes</Text>
            )}
            {post.caption ? (
              <View style={styles.captionRow}>
                <Text style={styles.captionUsername}>@{post.profile_username}</Text>
                <Text style={styles.captionText}>{post.caption}</Text>
              </View>
            ) : null}
            <Text style={styles.timestampText}>
              {new Date(post.timestamp).toLocaleDateString('en-US', { month: 'long', day: 'numeric' })}
            </Text>
          </View>
        </View>
      ))}

      <TouchableOpacity style={styles.refreshButton} onPress={loadFeed}>
        <Text style={styles.refreshButtonText}>Refresh</Text>
      </TouchableOpacity>

    </ScrollView>
  );
}
