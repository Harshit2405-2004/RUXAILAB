const {
  initializeApp: initializeAdminApp,
  cert,
} = require('firebase-admin/app')
const { getAuth } = require('firebase-admin/auth')
const { getFirestore } = require('firebase-admin/firestore')

// Set emulator environment variables before initializing admin SDK
process.env.FIREBASE_AUTH_EMULATOR_HOST = 'localhost:9099'
process.env.FIRESTORE_EMULATOR_HOST = 'localhost:8081'

const app = initializeAdminApp({
  projectId: 'ruxai-demo',
})

const auth = getAuth(app)
const db = getFirestore(app)

async function seed() {
  console.log('Seeding emulator data...')

  const email = 'dfa@dfa.com'
  const password = 'Dfa@1234'
  const uid = 'test-admin-uid-123'

  try {
    // 1. Create or Update Auth user
    let user
    try {
      user = await auth.getUserByEmail(email)
      console.log('User already exists in Auth emulator, skipping creation.')
    } catch (e) {
      user = await auth.createUser({
        uid: uid,
        email: email,
        password: password,
        displayName: 'Test Admin',
      })
      console.log('Created new user in Auth emulator:', user.uid)
    }

    // 2. Create or Update Firestore user document
    await db.collection('users').doc(user.uid).set({
      email: email,
      role: 'admin',
      name: 'Test Admin',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    })
    console.log(
      'Upserted user document in Firestore emulator collection "users"',
    )

    console.log('✅ Seeding complete. User "dfa@dfa.com" is now an admin.')
  } catch (error) {
    console.error('❌ Seeding failed:', error)
    process.exit(1)
  }
}

seed()
