import { StyleSheet } from 'react-native';

// color palette
const PINK = '#e1306c';
const PURPLE = '#833ab4';
const BLUE = '#405de6';
const LIGHT_BLUE = '#0095f6';
const BG = '#fafafa';
const WHITE = '#ffffff';
const BORDER = '#dbdbdb';
const TEXT = '#262626';
const GRAY = '#8e8e8e';

export const styles = StyleSheet.create({

  // ── login screen ──────────────────────────────────────────────
  loginWrapper: {
    flex: 1,
    backgroundColor: BG,
    paddingHorizontal: 36,
    paddingTop: 90,
    paddingBottom: 30,
    alignItems: 'center',
  },
  logoIcon: {
    fontSize: 60,
    marginBottom: 8,
  },
  logoText: {
    fontSize: 40,
    fontWeight: '300',
    fontStyle: 'italic',
    color: PURPLE,
    marginBottom: 36,
    letterSpacing: 1.5,
  },
  inputFull: {
    width: '100%',
    backgroundColor: '#fafafa',
    borderWidth: 1.5,
    borderColor: BORDER,
    borderRadius: 10,
    paddingVertical: 11,
    paddingHorizontal: 14,
    fontSize: 15,
    marginBottom: 10,
    color: TEXT,
  },
  loginButton: {
    width: '100%',
    backgroundColor: PINK,
    borderRadius: 10,
    paddingVertical: 13,
    alignItems: 'center',
    marginTop: 6,
    shadowColor: PINK,
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.3,
    shadowRadius: 6,
    elevation: 4,
  },
  loginButtonText: {
    color: WHITE,
    fontSize: 16,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  logoutButton: {
    width: '100%',
    borderWidth: 1.5,
    borderColor: BORDER,
    borderRadius: 10,
    paddingVertical: 12,
    alignItems: 'center',
    marginTop: 10,
    backgroundColor: WHITE,
  },
  logoutButtonText: {
    color: TEXT,
    fontSize: 15,
    fontWeight: '600',
  },
  dividerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 22,
    width: '100%',
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: BORDER,
  },
  dividerText: {
    color: GRAY,
    fontSize: 13,
    fontWeight: '600',
    marginHorizontal: 14,
  },
  loggedInCard: {
    width: '100%',
    backgroundColor: WHITE,
    borderRadius: 14,
    padding: 22,
    borderWidth: 1,
    borderColor: BORDER,
    alignItems: 'center',
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06,
    shadowRadius: 4,
    elevation: 2,
  },
  loggedInText: {
    fontSize: 17,
    color: TEXT,
    marginBottom: 4,
    fontWeight: '600',
  },
  loggedInSub: {
    fontSize: 13,
    color: GRAY,
  },

  // ── not logged in placeholder ─────────────────────────────────
  notLoggedIn: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 40,
    backgroundColor: BG,
  },
  notLoggedInText: {
    fontSize: 15,
    color: GRAY,
    textAlign: 'center',
    marginTop: 10,
  },

  // ── profile screen ────────────────────────────────────────────
  profileHeader: {
    backgroundColor: WHITE,
    paddingTop: 22,
    paddingHorizontal: 16,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: BORDER,
  },
  profileTopRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 14,
  },
  avatarLarge: {
    width: 88,
    height: 88,
    borderRadius: 44,
    marginRight: 24,
    borderWidth: 2.5,
    borderColor: PINK,
  },
  avatarPlaceholder: {
    width: 88,
    height: 88,
    borderRadius: 44,
    marginRight: 24,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2.5,
    borderColor: PINK,
    backgroundColor: '#f0d0da',
  },
  avatarPlaceholderText: {
    fontSize: 34,
    color: PINK,
    fontWeight: '700',
  },
  statsRow: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statItem: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 20,
    fontWeight: '700',
    color: TEXT,
  },
  statLabel: {
    fontSize: 12,
    color: TEXT,
    marginTop: 1,
  },
  profileName: {
    fontSize: 15,
    fontWeight: '700',
    color: TEXT,
    marginBottom: 3,
  },
  profileBio: {
    fontSize: 14,
    color: TEXT,
    lineHeight: 19,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 11,
    borderTopWidth: 1,
    borderTopColor: BORDER,
    backgroundColor: WHITE,
    marginTop: 6,
  },
  sectionHeaderText: {
    fontSize: 13,
    fontWeight: '700',
    color: TEXT,
    letterSpacing: 1.2,
  },

  // ── post cards ────────────────────────────────────────────────
  postCard: {
    backgroundColor: WHITE,
    borderBottomWidth: 1,
    borderBottomColor: BORDER,
  },
  postCardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 10,
  },
  avatarSmall: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#f0d0da',
    marginRight: 10,
    borderWidth: 1.5,
    borderColor: PINK,
  },
  avatarSmallImg: {
    width: 36,
    height: 36,
    borderRadius: 18,
    marginRight: 10,
  },
  postUsername: {
    fontSize: 14,
    fontWeight: '700',
    color: TEXT,
  },
  postImage: {
    width: '100%',
    height: 300,
    resizeMode: 'cover',
  },
  postFooter: {
    paddingHorizontal: 12,
    paddingTop: 10,
    paddingBottom: 14,
  },
  likesText: {
    fontSize: 14,
    fontWeight: '700',
    color: TEXT,
    marginBottom: 4,
  },
  captionRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 4,
  },
  captionUsername: {
    fontSize: 14,
    fontWeight: '700',
    color: TEXT,
    marginRight: 4,
  },
  captionText: {
    fontSize: 14,
    color: TEXT,
    flex: 1,
  },
  timestampText: {
    fontSize: 11,
    color: GRAY,
    marginTop: 5,
    textTransform: 'uppercase',
    letterSpacing: 0.3,
  },

  // ── create post screen ────────────────────────────────────────
  createWrapper: {
    flex: 1,
    backgroundColor: WHITE,
  },
  createHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderBottomWidth: 1,
    borderBottomColor: BORDER,
  },
  createHeaderTitle: {
    fontSize: 17,
    fontWeight: '700',
    color: TEXT,
  },
  shareButton: {
    paddingHorizontal: 4,
  },
  shareButtonText: {
    fontSize: 16,
    fontWeight: '700',
    color: LIGHT_BLUE,
  },
  createBody: {
    padding: 16,
  },
  imagePreviewBox: {
    width: '100%',
    height: 220,
    backgroundColor: '#f5f5f5',
    borderRadius: 12,
    overflow: 'hidden',
    marginBottom: 18,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: BORDER,
    borderStyle: 'dashed',
  },
  imagePreview: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  imagePreviewPlaceholder: {
    fontSize: 13,
    color: GRAY,
  },
  createLabel: {
    fontSize: 12,
    fontWeight: '700',
    color: GRAY,
    marginBottom: 6,
    textTransform: 'uppercase',
    letterSpacing: 0.8,
  },
  createInput: {
    borderWidth: 1.5,
    borderColor: BORDER,
    borderRadius: 10,
    paddingVertical: 10,
    paddingHorizontal: 13,
    marginBottom: 16,
    fontSize: 15,
    color: TEXT,
    backgroundColor: BG,
  },
  createTextArea: {
    borderWidth: 1.5,
    borderColor: BORDER,
    borderRadius: 10,
    paddingVertical: 10,
    paddingHorizontal: 13,
    marginBottom: 16,
    fontSize: 15,
    color: TEXT,
    height: 100,
    textAlignVertical: 'top',
    backgroundColor: BG,
  },
  createSubmitButton: {
    backgroundColor: PINK,
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: 'center',
    marginTop: 4,
    shadowColor: PINK,
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.3,
    shadowRadius: 6,
    elevation: 4,
  },
  createSubmitText: {
    color: WHITE,
    fontSize: 16,
    fontWeight: '700',
    letterSpacing: 0.4,
  },

  // ── refresh button ────────────────────────────────────────────
  refreshButton: {
    margin: 16,
    borderWidth: 1.5,
    borderColor: BORDER,
    borderRadius: 10,
    paddingVertical: 10,
    alignItems: 'center',
    backgroundColor: WHITE,
  },
  refreshButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: TEXT,
  },
});
