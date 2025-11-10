package com.billionsbounty.mobile.utils

import android.content.Context
import android.content.SharedPreferences
import com.billionsbounty.mobile.data.repository.ApiRepository
import com.billionsbounty.mobile.data.api.UserProfileResponse
import com.billionsbounty.mobile.ui.components.ActivityStorage
import com.billionsbounty.mobile.ui.components.ActivityType
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.runTest
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.ResponseBody
import org.junit.After
import org.junit.Before
import org.junit.Test
import org.mockito.Mock
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.*
import retrofit2.Response
import kotlin.test.*

/**
 * Unit tests for ActivityHelper
 * Tests activity tracking helper functions
 */
@OptIn(ExperimentalCoroutinesApi::class)
class ActivityHelperTest {

    @Mock
    private lateinit var mockContext: Context

    @Mock
    private lateinit var mockSharedPreferences: SharedPreferences

    @Mock
    private lateinit var mockEditor: SharedPreferences.Editor

    @Mock
    private lateinit var mockApiRepository: ApiRepository

    private lateinit var closeable: AutoCloseable

    @Before
    fun setup() {
        closeable = MockitoAnnotations.openMocks(this)
        
        // Setup SharedPreferences mocks
        whenever(mockContext.getSharedPreferences("bounty_activities", Context.MODE_PRIVATE))
            .thenReturn(mockSharedPreferences)
        whenever(mockSharedPreferences.edit()).thenReturn(mockEditor)
        whenever(mockEditor.putString(any(), any())).thenReturn(mockEditor)
    }

    @After
    fun tearDown() {
        closeable.close()
    }

    @Test
    fun `trackQuestion saves activity to storage`() {
        // Given
        whenever(mockSharedPreferences.getString("activities", null)).thenReturn(null)

        // When
        ActivityHelper.trackQuestion(
            context = mockContext,
            bountyId = 1,
            username = "testuser",
            bountyName = "Test Bounty",
            isFirstQuestion = false
        )

        // Then
        verify(mockEditor).putString(eq("activities"), any())
        verify(mockEditor).apply()
    }

    @Test
    fun `trackQuestion does not save when username is blank`() {
        // When
        ActivityHelper.trackQuestion(
            context = mockContext,
            bountyId = 1,
            username = "", // Blank username
            bountyName = "Test Bounty"
        )

        // Then
        verify(mockEditor, never()).putString(any(), any())
    }

    @Test
    fun `trackQuestion uses FIRST_QUESTION type when isFirstQuestion is true`() {
        // Given
        whenever(mockSharedPreferences.getString("activities", null)).thenReturn(null)

        // When
        ActivityHelper.trackQuestion(
            context = mockContext,
            bountyId = 1,
            username = "testuser",
            bountyName = "Test Bounty",
            isFirstQuestion = true
        )

        // Then
        verify(mockEditor).putString(eq("activities"), argThat { json: String ->
            json.contains("just asked their first question")
        })
    }

    @Test
    fun `trackQuestion uses QUESTION type when isFirstQuestion is false`() {
        // Given
        whenever(mockSharedPreferences.getString("activities", null)).thenReturn(null)

        // When
        ActivityHelper.trackQuestion(
            context = mockContext,
            bountyId = 1,
            username = "testuser",
            bountyName = "Test Bounty",
            isFirstQuestion = false
        )

        // Then
        verify(mockEditor).putString(eq("activities"), argThat { json: String ->
            json.contains("just asked Test Bounty")
        })
    }

    @Test
    fun `trackNftRedeem saves activity to storage`() {
        // Given
        whenever(mockSharedPreferences.getString("activities", null)).thenReturn(null)

        // When
        ActivityHelper.trackNftRedeem(
            context = mockContext,
            bountyId = 1,
            username = "testuser"
        )

        // Then
        verify(mockEditor).putString(eq("activities"), argThat { json: String ->
            json.contains("redeemed their NFT")
        })
        verify(mockEditor).apply()
    }

    @Test
    fun `trackReferral saves activity to storage`() {
        // Given
        whenever(mockSharedPreferences.getString("activities", null)).thenReturn(null)

        // When
        ActivityHelper.trackReferral(
            context = mockContext,
            bountyId = 1,
            username = "testuser"
        )

        // Then
        verify(mockEditor).putString(eq("activities"), argThat { json: String ->
            json.contains("referred a new friend")
        })
        verify(mockEditor).apply()
    }

    @Test
    fun `getUsername returns display_name when available`() = runTest {
        // Given
        val mockResponse = Response.success(
            UserProfileResponse(
                success = true,
                user_id = 1,
                wallet_address = "test123",
                display_name = "TestUser",
                username = null
            )
        )
        whenever(mockApiRepository.getUserProfile("test123")).thenReturn(mockResponse)

        // When
        val username = ActivityHelper.getUsername(mockContext, "test123", mockApiRepository)

        // Then
        assertEquals("TestUser", username)
    }

    @Test
    fun `getUsername returns username when display_name is null`() = runTest {
        // Given
        val mockResponse = Response.success(
            UserProfileResponse(
                success = true,
                user_id = 1,
                wallet_address = "test123",
                display_name = null,
                username = "FallbackUser"
            )
        )
        whenever(mockApiRepository.getUserProfile("test123")).thenReturn(mockResponse)

        // When
        val username = ActivityHelper.getUsername(mockContext, "test123", mockApiRepository)

        // Then
        assertEquals("FallbackUser", username)
    }

    @Test
    fun `getUsername returns null when wallet address is blank`() = runTest {
        // When
        val username = ActivityHelper.getUsername(mockContext, "", mockApiRepository)

        // Then
        assertNull(username)
        verify(mockApiRepository, never()).getUserProfile(any())
    }

    @Test
    fun `getUsername returns null when API call fails`() = runTest {
        // Given - API call throws exception (suspend function needs proper mocking)
        // We'll use a simpler test that mocks the Response as unsuccessful instead
        val mockResponse = Response.error<UserProfileResponse>(500, 
            okhttp3.ResponseBody.create("application/json".toMediaType(), "{}"))
        whenever(mockApiRepository.getUserProfile("test123")).thenReturn(mockResponse)

        // When
        val username = ActivityHelper.getUsername(mockContext, "test123", mockApiRepository)

        // Then - should return null when response is not successful
        assertNull(username)
    }

    @Test
    fun `getUsername returns null when profile has no username or display_name`() = runTest {
        // Given
        val mockResponse = Response.success(
            UserProfileResponse(
                success = true,
                user_id = 1,
                wallet_address = "test123",
                display_name = null,
                username = null
            )
        )
        whenever(mockApiRepository.getUserProfile("test123")).thenReturn(mockResponse)

        // When
        val username = ActivityHelper.getUsername(mockContext, "test123", mockApiRepository)

        // Then
        assertNull(username)
    }

    @Test
    fun `isFirstQuestion returns true when no previous questions`() {
        // Given
        whenever(mockSharedPreferences.getString("activities", null)).thenReturn(null)

        // When
        val isFirst = ActivityHelper.isFirstQuestion(mockContext, 1, "testuser")

        // Then
        assertTrue(isFirst)
    }

    @Test
    fun `isFirstQuestion returns false when previous question exists`() {
        // Given
        val json = """
            [
                {"id": "1", "username": "testuser", "message": "just asked Test Bounty", "timestamp": ${System.currentTimeMillis()}, "bountyId": 1}
            ]
        """.trimIndent()
        whenever(mockSharedPreferences.getString("activities", null)).thenReturn(json)

        // When
        val isFirst = ActivityHelper.isFirstQuestion(mockContext, 1, "testuser")

        // Then
        assertFalse(isFirst)
    }

    @Test
    fun `isFirstQuestion returns true when previous question is for different user`() {
        // Given
        val json = """
            [
                {"id": "1", "username": "otheruser", "message": "just asked Test Bounty", "timestamp": ${System.currentTimeMillis()}, "bountyId": 1}
            ]
        """.trimIndent()
        whenever(mockSharedPreferences.getString("activities", null)).thenReturn(json)

        // When
        val isFirst = ActivityHelper.isFirstQuestion(mockContext, 1, "testuser")

        // Then
        assertTrue(isFirst)
    }
}

