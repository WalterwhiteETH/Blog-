# Frontend Migration Guide: Refactored Backend Integration

## 🎯 Overview

This guide helps you migrate the frontend to work with the new refactored backend architecture that separates payment and music domains.

## 🏗️ New Architecture

### Backend Services
- **Payment API**: `http://localhost:8001` - Payment processing and Ethiopian providers
- **Music API**: `http://localhost:8002` - Music functionality and marketplace
- **Legacy API**: `http://localhost:8000` - Original backend (fallback)

### Frontend Files Created
- `refactored-client.ts` - New API client for domain-based architecture
- `RefactoredPayments.tsx` - Updated payments page
- `RefactoredMarketplace.tsx` - Updated marketplace page
- `.env.example` - Environment configuration

## 🚀 Migration Steps

### 1. Environment Setup

```bash
# Copy the new environment configuration
cp .env.example .env

# Edit with your local configuration
nano .env
```

### 2. Update API Client

Replace old API calls with new domain-based calls:

**Old Way:**
```typescript
import { createPayment, purchaseSong } from '/@/renderer/api/client';
```

**New Way:**
```typescript
import { 
    createPaymentIntent, 
    purchaseSong, 
    processPayment,
    handleApiError 
} from '/@/renderer/api/refactored-client';
```

### 3. Update Payment Flow

**Old Payment Flow:**
```typescript
const result = await createPayment({
    amount: 99,
    method: 'telebirr',
    type: 'subscription_monthly',
    user_id: userId,
});
```

**New Payment Flow:**
```typescript
// Step 1: Create subscription purchase
const purchaseResult = await purchaseSubscription('premium', 'telebirr');

// Step 2: Process payment
const processResult = await processPayment(purchaseResult.payment_intent.id, {
    payment_provider: 'telebirr',
    return_url: `${window.location.origin}/payments/success`,
    cancel_url: `${window.location.origin}/payments/cancel`,
});

// Step 3: Handle redirect or verification
if (processResult.payment_url) {
    window.location.href = processResult.payment_url;
}
```

### 4. Update Marketplace Integration

**Old Marketplace:**
```typescript
const songs = await getMarketplaceSongs();
const playlists = await getMarketplacePlaylists();
```

**New Marketplace:**
```typescript
// Get marketplace listings
const listings = await getMarketplaceListings({
    limit: 50,
    item_type: 'song'
});

// Purchase with payment integration
const purchaseResult = await purchaseSong(songId, 'telebirr');
```

## 📋 Key Changes

### Payment Domain Integration
- ✅ **Ethiopian Providers**: Telebirr, Chapa, CBE Bank, Manual Bank
- ✅ **Payment Intents**: Professional payment flow with idempotency
- ✅ **Webhook Support**: Automatic payment verification
- ✅ **Security**: Signature verification and rate limiting

### Music Domain Features
- ✅ **Clean Separation**: No payment coupling in music domain
- ✅ **Rich Metadata**: Songs, playlists, artists, releases
- ✅ **Social Features**: Likes, follows, sharing
- ✅ **Marketplace**: Professional buying/selling flow

### Error Handling
- ✅ **Structured Errors**: Professional error responses
- ✅ **Type Safety**: Full TypeScript support
- ✅ **Retry Logic**: Built-in retry mechanisms
- ✅ **User Feedback**: Clear toast notifications

## 🔧 Configuration

### Environment Variables

```typescript
// Payment API
VITE_PAYMENT_API_URL=http://localhost:8001

// Music API  
VITE_MUSIC_API_URL=http://localhost:8002

// Feature Flags
VITE_ENABLE_NEW_PAYMENT_DOMAIN=true
VITE_ENABLE_NEW_MUSIC_DOMAIN=true
```

### API Client Features

```typescript
// Multiple domain support
const paymentClient = axios.create({ baseURL: PAYMENT_API_URL });
const musicClient = axios.create({ baseURL: MUSIC_API_URL });

// Automatic auth injection
addAuthInterceptor(paymentClient);
addAuthInterceptor(musicClient);

// Error handling
const error = handleApiError(apiError);
```

## 🧪 Testing

### 1. API Connectivity

```typescript
// Test new APIs
const migration = await migrateToNewAPI();
console.log('Payment API:', migration.payment_api_available);
console.log('Music API:', migration.music_api_available);
```

### 2. Payment Flow

```typescript
// Test subscription purchase
const result = await purchaseSubscription('premium', 'telebirr');
console.log('Purchase result:', result);
```

### 3. Marketplace

```typescript
// Test marketplace listings
const listings = await getMarketplaceListings();
console.log('Available items:', listings.items);
```

## 🔄 Migration Strategy

### Phase 1: Setup (Day 1)
- [ ] Copy new frontend files
- [ ] Update environment configuration
- [ ] Test API connectivity
- [ ] Verify payment providers

### Phase 2: Core Migration (Day 2-3)
- [ ] Update payment pages to use new client
- [ ] Update marketplace to use new APIs
- [ ] Test payment flows end-to-end
- [ ] Update error handling

### Phase 3: Advanced Features (Day 4-5)
- [ ] Add social features integration
- [ ] Implement search functionality
- [ ] Add analytics and tracking
- [ ] Test Ethiopian payment methods

### Phase 4: Production Ready (Day 6-7)
- [ ] Performance optimization
- [ ] Security testing
- [ ] Documentation updates
- [ ] User acceptance testing

## 🚨 Breaking Changes

### Removed Functions
- `createPayment()` → Replace with `purchaseSubscription()`
- `getMarketplaceSongs()` → Replace with `getMarketplaceListings()`
- `purchaseSong()` → Updated with payment integration

### Updated Signatures
- Payment functions now return `PaymentIntent` objects
- Marketplace functions include pagination
- Error handling uses structured responses

## 🎯 Benefits

### For Developers
- **Type Safety**: Full TypeScript support
- **Domain Separation**: Clear API boundaries
- **Error Handling**: Professional error management
- **Testing**: Comprehensive test utilities

### For Users
- **Ethiopian Payments**: Local payment methods
- **Better UX**: Clear payment flows
- **Social Features**: Enhanced interaction
- **Performance**: Faster, more reliable

### For Business
- **Scalability**: Clean domain architecture
- **Security**: Enterprise-grade controls
- **Compliance**: Ethiopian payment standards
- **Analytics**: Comprehensive tracking

## 📞 Support

### Migration Issues
- Check browser console for API errors
- Verify environment variables
- Test with different payment providers
- Review network requests in dev tools

### Common Problems
1. **CORS Issues**: Ensure backend allows frontend origin
2. **Auth Failures**: Check token storage and retrieval
3. **Payment Errors**: Verify provider configuration
4. **Network Timeouts**: Adjust timeout settings

## 🎉 Success Criteria

Migration is complete when:
- ✅ All payment flows work with new APIs
- ✅ Marketplace displays items correctly
- ✅ Ethiopian payment providers function
- ✅ Error handling shows user-friendly messages
- ✅ Performance meets or exceeds current benchmarks
- ✅ Security controls are active

## 📚 Additional Resources

- [Payment API Documentation](http://localhost:8001/docs)
- [Music API Documentation](http://localhost:8002/docs)
- [Backend Refactoring Summary](./PHASE2_MUSIC_REFACTORING_SUMMARY.md)
- [Code Analysis Report](./CODE_ANALYSIS_REPORT.md)

---

**🚀 Your frontend is now ready to work with the new refactored backend architecture!**
