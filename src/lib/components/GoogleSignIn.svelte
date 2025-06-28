<script>
	import { onMount, getContext } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { authenticateWithGoogle } from '$lib/apis/auths';
	import { goto } from '$app/navigation';
	import { getBackendConfig } from '$lib/apis';
	import { WEBUI_NAME, config, user, socket } from '$lib/stores';

	const i18n = getContext('i18n');

	// Google Client ID - hardcoded as requested
	const GOOGLE_CLIENT_ID = '43207891529-ha7i7kbngq6mdth2aicle5j7v1ac26ub.apps.googleusercontent.com';
	
	let googleInitialized = false;
	let isAuthenticating = false;

	const querystringValue = (key) => {
		const querystring = window.location.search;
		const urlParams = new URLSearchParams(querystring);
		return urlParams.get(key);
	};

	const setSessionUser = async (sessionUser) => {
		if (sessionUser) {
			console.log(sessionUser);
			toast.success($i18n.t(`You're now logged in.`));
			if (sessionUser.token) {
				localStorage.token = sessionUser.token;
			}
			$socket.emit('user-join', { auth: { token: sessionUser.token } });
			await user.set(sessionUser);
			await config.set(await getBackendConfig());

			const redirectPath = querystringValue('redirect') || '/';
			goto(redirectPath);
		}
	};

	const initializeGoogleSignIn = () => {
		if (typeof window === 'undefined' || googleInitialized) return;

		// Load Google Identity Services script
		const script = document.createElement('script');
		script.src = 'https://accounts.google.com/gsi/client';
		script.async = true;
		script.defer = true;
		script.onload = () => {
			googleInitialized = true;
			renderGoogleSignIn();
		};
		document.head.appendChild(script);
	};

	const renderGoogleSignIn = () => {
		if (typeof window === 'undefined' || !window.google) return;

		// Clear existing button
		const container = document.getElementById('google-signin-container');
		if (container) {
			container.innerHTML = '';
		}

		// Create Google Sign-In button
		window.google.accounts.id.initialize({
			client_id: GOOGLE_CLIENT_ID,
			callback: handleGoogleSignIn
		});

		window.google.accounts.id.renderButton(
			document.getElementById('google-signin-container'),
			{
				type: 'standard',
				theme: 'outline',
				size: 'large',
				text: 'continue_with',
				shape: 'rectangular',
				logo_alignment: 'center',
				width: 250
			}
		);

		// Enable One Tap
		window.google.accounts.id.prompt();
	};

	const handleGoogleSignIn = async (response) => {
		if (isAuthenticating) return;
		
		isAuthenticating = true;
		
		try {
			const { credential } = response;
			
			// Call our backend with the Google token
			const sessionUser = await authenticateWithGoogle(credential);
			await setSessionUser(sessionUser);
		} catch (error) {
			console.error('Google sign-in error:', error);
			toast.error($i18n.t('Google sign-in failed. Please try again.'));
		} finally {
			isAuthenticating = false;
		}
	};

	const handleManualGoogleSignIn = async () => {
		if (isAuthenticating) return;
		
		isAuthenticating = true;
		
		try {
			// For manual sign-in, we'll use a mock token for testing
			// In production, this should be replaced with actual Google OAuth flow
			const mockToken = 'mock_google_token_for_testing';
			const sessionUser = await authenticateWithGoogle(mockToken);
			await setSessionUser(sessionUser);
		} catch (error) {
			console.error('Manual Google sign-in error:', error);
			toast.error($i18n.t('Google sign-in failed. Please try again.'));
		} finally {
			isAuthenticating = false;
		}
	};

	onMount(() => {
		initializeGoogleSignIn();
	});
</script>

<div class="w-full flex flex-col items-center">
	<!-- Google Sign-In Button Container -->
	<div 
		id="google-signin-container" 
		class="w-full flex justify-center"
	>
		<!-- Fallback button if Google script doesn't load -->
		<button
			class="flex justify-center items-center bg-white hover:bg-gray-50 text-gray-700 border border-gray-300 rounded-lg px-4 py-2 font-medium text-sm transition w-full max-w-[250px] disabled:opacity-50 disabled:cursor-not-allowed"
			on:click={handleManualGoogleSignIn}
			disabled={isAuthenticating}
		>
			{#if isAuthenticating}
				<div class="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-700 mr-2"></div>
			{:else}
				<svg class="w-5 h-5 mr-2" viewBox="0 0 24 24">
					<path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
					<path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
					<path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
					<path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
				</svg>
			{/if}
			<span>{isAuthenticating ? $i18n.t('Signing in...') : $i18n.t('Continue with Google')}</span>
		</button>
	</div>

	<!-- Loading indicator for Google script -->
	{#if !googleInitialized}
		<div class="mt-2 text-xs text-gray-500">
			{$i18n.t('Loading Google Sign-In...')}
		</div>
	{/if}
</div>

<style>
	/* Custom styles for Google Sign-In button */
	:global(#google-signin-container) {
		display: flex;
		justify-content: center;
		align-items: center;
	}
</style> 