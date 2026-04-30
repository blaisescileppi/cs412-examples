// Search screen - find and follow/unfollow other users

import { useState } from 'react';
import { View, Text, Image, TextInput, TouchableOpacity, FlatList, ActivityIndicator } from 'react-native';
import { StyleSheet } from 'react-native';
import { useAuth } from '@/contexts/AuthContext';

const API_BASE = 'http://127.0.0.1:8000/mini_insta/api';

export default function SearchScreen() {
  const { token } = useAuth();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const search = async () => {
    if (!query.trim() || !token) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/search/?q=${encodeURIComponent(query)}`, {
        headers: { 'Authorization': `Token ${token}` },
      });
      const data = await res.json();
      setResults(data);
      console.log('Search results:', data.length);
    } catch (e) {
      console.log('Search error:', e);
    }
    setLoading(false);
  };

  const toggleFollow = async (profile: any) => {
    const endpoint = profile.is_following ? 'unfollow' : 'follow';
    try {
      await fetch(`${API_BASE}/profiles/${profile.id}/${endpoint}/`, {
        method: 'POST',
        headers: { 'Authorization': `Token ${token}` },
      });
      // update local state so button flips immediately
      setResults(prev =>
        prev.map(p =>
          p.id === profile.id ? { ...p, is_following: !p.is_following } : p
        )
      );
    } catch (e) {
      console.log('Follow error:', e);
    }
  };

  if (!token) {
    return (
      <View style={ss.notLoggedIn}>
        <Text style={{ fontSize: 40 }}>🔒</Text>
        <Text style={ss.notLoggedInText}>Log in to search for people.</Text>
      </View>
    );
  }

  return (
    <View style={{ flex: 1, backgroundColor: '#fafafa' }}>

      {/* Search bar */}
      <View style={ss.searchBar}>
        <TextInput
          style={ss.searchInput}
          value={query}
          onChangeText={setQuery}
          placeholder="Search people..."
          autoCapitalize="none"
          autoCorrect={false}
          placeholderTextColor="#aaa"
          onSubmitEditing={search}
          returnKeyType="search"
        />
        <TouchableOpacity style={ss.searchButton} onPress={search}>
          <Text style={ss.searchButtonText}>Search</Text>
        </TouchableOpacity>
      </View>

      {loading && <ActivityIndicator style={{ marginTop: 20 }} color="#0095f6" />}

      {results.length === 0 && !loading && query.trim() !== '' && (
        <View style={ss.empty}>
          <Text style={ss.emptyText}>No results for &quot;{query}&quot;</Text>
        </View>
      )}

      <FlatList
        data={results}
        keyExtractor={(item) => String(item.id)}
        renderItem={({ item }) => (
          <View style={ss.resultRow}>

            {/* Avatar */}
            {item.profile_image_url ? (
              <Image source={{ uri: item.profile_image_url }} style={ss.avatar} />
            ) : (
              <View style={ss.avatarPlaceholder}>
                <Text style={ss.avatarLetter}>
                  {item.username ? item.username[0].toUpperCase() : '?'}
                </Text>
              </View>
            )}

            {/* Name info */}
            <View style={ss.nameCol}>
              <Text style={ss.username}>@{item.username}</Text>
              <Text style={ss.displayName}>{item.display_name}</Text>
              <Text style={ss.followerCount}>{item.num_followers} followers</Text>
            </View>

            {/* Follow / Unfollow button */}
            <TouchableOpacity
              style={item.is_following ? ss.unfollowBtn : ss.followBtn}
              onPress={() => toggleFollow(item)}>
              <Text style={item.is_following ? ss.unfollowBtnText : ss.followBtnText}>
                {item.is_following ? 'Following' : 'Follow'}
              </Text>
            </TouchableOpacity>

          </View>
        )}
        ItemSeparatorComponent={() => <View style={ss.separator} />}
      />
    </View>
  );
}

const ss = StyleSheet.create({
  notLoggedIn: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 40,
  },
  notLoggedInText: {
    fontSize: 16,
    color: '#8e8e8e',
    marginTop: 10,
    textAlign: 'center',
  },
  searchBar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#dbdbdb',
    paddingHorizontal: 12,
    paddingVertical: 10,
    gap: 8,
  },
  searchInput: {
    flex: 1,
    backgroundColor: '#efefef',
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 8,
    fontSize: 15,
    color: '#262626',
  },
  searchButton: {
    paddingHorizontal: 4,
  },
  searchButtonText: {
    fontSize: 15,
    fontWeight: '700',
    color: '#0095f6',
  },
  empty: {
    padding: 30,
    alignItems: 'center',
  },
  emptyText: {
    color: '#8e8e8e',
    fontSize: 14,
  },
  resultRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: 'white',
  },
  avatar: {
    width: 50,
    height: 50,
    borderRadius: 25,
    marginRight: 12,
  },
  avatarPlaceholder: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#c7c7c7',
    marginRight: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarLetter: {
    fontSize: 20,
    color: 'white',
    fontWeight: '600',
  },
  nameCol: {
    flex: 1,
  },
  username: {
    fontSize: 14,
    fontWeight: '700',
    color: '#262626',
  },
  displayName: {
    fontSize: 13,
    color: '#262626',
    marginTop: 1,
  },
  followerCount: {
    fontSize: 12,
    color: '#8e8e8e',
    marginTop: 1,
  },
  followBtn: {
    backgroundColor: '#0095f6',
    borderRadius: 8,
    paddingHorizontal: 18,
    paddingVertical: 7,
  },
  followBtnText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '700',
  },
  unfollowBtn: {
    backgroundColor: 'white',
    borderRadius: 8,
    paddingHorizontal: 14,
    paddingVertical: 7,
    borderWidth: 1,
    borderColor: '#dbdbdb',
  },
  unfollowBtnText: {
    color: '#262626',
    fontSize: 14,
    fontWeight: '600',
  },
  separator: {
    height: 1,
    backgroundColor: '#dbdbdb',
    marginLeft: 78,
  },
});
