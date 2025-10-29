package com.billionsbounty.mobile.repository

import com.billionsbounty.mobile.data.api.ApiClient
import com.billionsbounty.mobile.data.api.NftStatusResponse
import com.billionsbounty.mobile.data.api.NftVerifyRequest
import com.billionsbounty.mobile.data.api.NftVerifyResponse
import com.billionsbounty.mobile.data.repository.NftRepository
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.runTest
import org.junit.Before
import org.junit.Test
import org.mockito.Mock
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.any
import org.mockito.kotlin.whenever
import retrofit2.Response
import kotlin.test.assertEquals
import kotlin.test.assertTrue

@OptIn(ExperimentalCoroutinesApi::class)
class NftRepositoryTest {

    @Mock
    private lateinit var apiClient: ApiClient

    private lateinit var repository: NftRepository
    private lateinit var closeable: AutoCloseable

    @Before
    fun setup() {
        closeable = MockitoAnnotations.openMocks(this)
        repository = NftRepository(apiClient)
    }

    @Test
    fun `checkNftOwnership returns success with mock mode`() = runTest {
        val mockResponse = NftStatusResponse(
            success = true,
            has_nft = true,
            verified = false,
            is_mock = true,
            questions_remaining = 0,
            message = "Mock NFT found"
        )
        
        whenever(apiClient.getNftStatus(any()))
            .thenReturn(Response.success(mockResponse))

        val result = repository.checkNftOwnership("TestWallet123")

        assertTrue(result.isSuccess)
        val response = result.getOrNull()!!
        assertTrue(response.success)
        assertTrue(response.has_nft)
        assertTrue(response.is_mock)
    }

    @Test
    fun `checkNftOwnership returns failure on error`() = runTest {
        whenever(apiClient.getNftStatus(any()))
            .thenReturn(Response.error(404, okhttp3.ResponseBody.create(null, "")))

        val result = repository.checkNftOwnership("TestWallet123")

        assertTrue(result.isFailure)
    }

    @Test
    fun `getNftStatus returns verified status`() = runTest {
        val mockResponse = NftStatusResponse(
            success = true,
            has_nft = true,
            verified = true,
            is_mock = false,
            questions_remaining = 5,
            message = "NFT verified"
        )
        
        whenever(apiClient.getNftStatus(any()))
            .thenReturn(Response.success(mockResponse))

        val result = repository.getNftStatus("TestWallet123")

        assertTrue(result.isSuccess)
        val response = result.getOrNull()!!
        assertTrue(response.verified)
        assertEquals(5, response.questions_remaining)
    }

    @Test
    fun `verifyNftOwnership grants questions in mock mode`() = runTest {
        val mockResponse = NftVerifyResponse(
            success = true,
            verified = true,
            is_mock = true,
            questions_granted = 5,
            questions_remaining = 5,
            message = "Mock verification successful - 5 free questions granted"
        )
        
        whenever(apiClient.verifyNft(any()))
            .thenReturn(Response.success(mockResponse))

        val result = repository.verifyNftOwnership(
            walletAddress = "TestWallet123",
            signature = "mock_signature"
        )

        assertTrue(result.isSuccess)
        val response = result.getOrNull()!!
        assertTrue(response.verified)
        assertTrue(response.is_mock)
        assertEquals(5, response.questions_granted)
    }

    @Test
    fun `verifyNftOwnership handles verification failure`() = runTest {
        val mockResponse = NftVerifyResponse(
            success = false,
            verified = false,
            is_mock = false,
            questions_granted = 0,
            questions_remaining = 0,
            message = "NFT not found"
        )
        
        whenever(apiClient.verifyNft(any()))
            .thenReturn(Response.success(mockResponse))

        val result = repository.verifyNftOwnership(
            walletAddress = "TestWallet123",
            signature = "test_signature"
        )

        assertTrue(result.isSuccess)
        val response = result.getOrNull()!!
        assertTrue(!response.verified)
        assertEquals(0, response.questions_granted)
    }

    @Test
    fun `verifyNftOwnership returns failure on network error`() = runTest {
        whenever(apiClient.verifyNft(any()))
            .thenReturn(Response.error(500, okhttp3.ResponseBody.create(null, "")))

        val result = repository.verifyNftOwnership(
            walletAddress = "TestWallet123",
            signature = "test_signature"
        )

        assertTrue(result.isFailure)
    }

    @Test
    fun `AUTHORIZED_NFT_MINT constant is correct`() {
        assertEquals(
            "9dBdXMB3WuTy638W1a1tTygWCzosUmALhRLksrX8oQVa",
            NftRepository.AUTHORIZED_NFT_MINT
        )
    }
}

