// Profile screen - shows logged in user's profile info and posts

import { useEffect, useState } from 'react';
import { View, Text, Image, ScrollView, TouchableOpacity } from 'react-native';
import { styles } from '../../assets/my_styles';
import { useAuth } from '@/contexts/AuthContext';

const API_BASE = 'http://127.0.0.1:8000/mini_insta/api';

export default function ProfileScreen() {
  const { token, profileId } = useAuth();
  const [profile, setProfile] = useState<any>(null);
  const [posts, setPosts] = useState<any[]>([]);

  const loadProfile = async () => {
    if (!profileId || !token) return;
    try {
      const res = await fetch(`${API_BASE}/profiles/${profileId}/`, {
        headers: { 'Authorization': `Token ${token}` },
      });
      const data = await res.json();
      setProfile(data);
    } catch (e) {
      console.log('Error loading profile:', e);
    }
  };

  const loadPosts = async () => {
    if (!profileId || !token) return;
    try {
      const res = await fetch(`${API_BASE}/profiles/${profileId}/posts/`, {
        headers: { 'Authorization': `Token ${token}` },
      });
      const data = await res.json();
      setPosts(data);
    } catch (e) {
      console.log('Error loading posts:', e);
    }
  };

  useEffect(() => {
    if (profileId) {
      loadProfile();
      loadPosts();
    }
  }, [profileId]);

  if (!token) {
    return (
      <View style={styles.notLoggedIn}>
        <Text style={{ fontSize: 40 }}>🔒</Text>
        <Text style={styles.notLoggedInText}>Log in to see your profile.</Text>
      </View>
    );
  }

  return (
    <ScrollView style={{ backgroundColor: '#fafafa' }}>

      {/* Profile header */}
      {profile && (
        <View style={styles.profileHeader}>
          <View style={styles.profileTopRow}>

            {/* Avatar */}
            {profile.profile_image_url ? (
              <Image source={{ uri: profile.profile_image_url }} style={styles.avatarLarge} />
            ) : (
              <View style={styles.avatarPlaceholder}>
                <Text style={styles.avatarPlaceholderText}>
                  {profile.username ? profile.username[0].toUpperCase() : '?'}
                </Text>
              </View>
            )}

            {/* Stats */}
            <View style={styles.statsRow}>
              <View style={styles.statItem}>
                <Text style={styles.statNumber}>{posts.length}</Text>
                <Text style={styles.statLabel}>posts</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statNumber}>{profile.num_followers}</Text>
                <Text style={styles.statLabel}>followers</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statNumber}>{profile.num_following}</Text>
                <Text style={styles.statLabel}>following</Text>
              </View>
            </View>
          </View>

          {/* Name + bio */}
          <Text style={styles.profileName}>{profile.display_name}</Text>
          {profile.bio_text ? (
            <Text style={styles.profileBio}>{profile.bio_text}</Text>
          ) : null}
        </View>
      )}

      {/* Posts section label */}
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionHeaderText}>POSTS</Text>
      </View>

      {/* Posts */}
      {posts.length === 0 && (
        <View style={{ padding: 40, alignItems: 'center' }}>
          <Text style={{ fontSize: 36 }}>📷</Text>
          <Text style={{ color: '#8e8e8e', marginTop: 8, fontSize: 14 }}>No posts yet</Text>
        </View>
      )}

      {posts.map((post) => (
        <View key={post.id} style={styles.postCard}>
          {/* Post images */}
          {post.photos && post.photos.map((photo: any) =>
            photo.image ? (
              <Image key={photo.id} source={{ uri: photo.image }} style={styles.postImage} />
            ) : null
          )}

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

      <TouchableOpacity
        style={styles.refreshButton}
        onPress={() => { loadProfile(); loadPosts(); }}>
        <Text style={styles.refreshButtonText}>Refresh</Text>
      </TouchableOpacity>

    </ScrollView>
  );
}
