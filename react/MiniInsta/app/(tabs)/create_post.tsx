// Create post screen

import { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, Alert, Image, ScrollView } from 'react-native';
import { styles } from '../../assets/my_styles';
import { useAuth } from '@/contexts/AuthContext';

const API_BASE = 'http://127.0.0.1:8000/mini_insta/api';

export default function CreatePostScreen() {
  const { token } = useAuth();
  const [caption, setCaption] = useState('');
  const [imageUrl, setImageUrl] = useState('');

  const submitPost = async () => {
    if (!caption.trim()) {
      Alert.alert('Missing caption', 'Please write something for your post.');
      return;
    }

    const payload: any = { caption };
    if (imageUrl.trim()) {
      payload.image_url = imageUrl.trim();
    }

    try {
      const response = await fetch(`${API_BASE}/post/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${token}`,
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (response.ok) {
        Alert.alert('Posted!', 'Your post was shared.');
        setCaption('');
        setImageUrl('');
      } else {
        Alert.alert('Error', 'Something went wrong.');
      }
    } catch (error) {
      console.log('Create post error:', error);
      Alert.alert('Error', 'Could not reach the server.');
    }
  };

  if (!token) {
    return (
      <View style={styles.notLoggedIn}>
        <Text style={{ fontSize: 40 }}>🔒</Text>
        <Text style={styles.notLoggedInText}>Log in to create a post.</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.createWrapper}>

      {/* Fake nav header */}
      <View style={styles.createHeader}>
        <Text style={styles.createHeaderTitle}>New Post</Text>
        <TouchableOpacity style={styles.shareButton} onPress={submitPost}>
          <Text style={styles.shareButtonText}>Share</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.createBody}>

        {/* Image preview */}
        <View style={styles.imagePreviewBox}>
          {imageUrl.trim() ? (
            <Image source={{ uri: imageUrl.trim() }} style={styles.imagePreview} />
          ) : (
            <Text style={styles.imagePreviewPlaceholder}>Image preview will appear here</Text>
          )}
        </View>

        {/* Image URL */}
        <Text style={styles.createLabel}>Image URL</Text>
        <TextInput
          style={styles.createInput}
          value={imageUrl}
          onChangeText={setImageUrl}
          placeholder="https://..."
          autoCapitalize="none"
          autoCorrect={false}
          keyboardType="url"
          placeholderTextColor="#aaa"
        />

        {/* Caption */}
        <Text style={styles.createLabel}>Caption</Text>
        <TextInput
          style={styles.createTextArea}
          value={caption}
          onChangeText={setCaption}
          placeholder="Write a caption..."
          multiline
          placeholderTextColor="#aaa"
        />

        <TouchableOpacity style={styles.createSubmitButton} onPress={submitPost}>
          <Text style={styles.createSubmitText}>Share Post</Text>
        </TouchableOpacity>

      </View>
    </ScrollView>
  );
}
