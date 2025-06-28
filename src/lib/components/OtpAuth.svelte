<script>
	import { toast } from 'svelte-sonner';
	import { getContext } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';

	import { sendOtp, verifyOtp } from '$lib/apis/auths';
	import { WEBUI_NAME, config, user, socket } from '$lib/stores';
	import { getBackendConfig } from '$lib/apis';

	import Spinner from './common/Spinner.svelte';
	import ArrowLeft from './icons/ArrowLeft.svelte';
	import GoogleSignIn from './GoogleSignIn.svelte';

	const i18n = getContext('i18n');

	export let onBack = () => {};
	export let onSuccess = () => {};

	let phone = '';
	let otpCode = '';
	let session = '';
	let isSendingOtp = false;
	let isVerifyingOtp = false;
	let otpSent = false;
	let countdown = 0;
	let countdownInterval;

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

	const startCountdown = () => {
		countdown = 60;
		countdownInterval = setInterval(() => {
			countdown--;
			if (countdown <= 0) {
				clearInterval(countdownInterval);
			}
		}, 1000);
	};

	const formatPhoneNumber = (value) => {
		// Remove all non-digit characters
		const cleaned = value.replace(/\D/g, '');
		
		// Limit to 10 digits
		const limited = cleaned.slice(0, 10);
		
		// Format as (XXX) XXX-XXXX for display
		if (limited.length <= 3) {
			return limited;
		} else if (limited.length <= 6) {
			return `(${limited.slice(0, 3)}) ${limited.slice(3)}`;
		} else {
			return `(${limited.slice(0, 3)}) ${limited.slice(3, 6)}-${limited.slice(6, 10)}`;
		}
	};

	const getFormattedPhoneForAPI = (displayPhone) => {
		// Remove all non-digit characters and get only digits
		const digits = displayPhone.replace(/\D/g, '');
		
		// Ensure exactly 10 digits
		if (digits.length === 10) {
			return `+91${digits}`;
		}
		return null;
	};

	const handlePhoneInput = (event) => {
		const formatted = formatPhoneNumber(event.target.value);
		phone = formatted;
	};

	const handleSendOtp = async () => {
		const apiPhone = getFormattedPhoneForAPI(phone);
		if (!apiPhone) {
			toast.error($i18n.t('Please enter a valid 10-digit phone number'));
			return;
		}

		isSendingOtp = true;
		try {
			const response = await sendOtp(apiPhone);
			if (response.success) {
				session = response.session;
				otpSent = true;
				startCountdown();
				toast.success($i18n.t('OTP sent successfully'));
			} else {
				toast.error(response.message || $i18n.t('Failed to send OTP'));
			}
		} catch (error) {
			toast.error(error || $i18n.t('Failed to send OTP'));
		} finally {
			isSendingOtp = false;
		}
	};

	const handleVerifyOtp = async () => {
		if (!otpCode || otpCode.length < 4) {
			toast.error($i18n.t('Please enter a valid OTP'));
			return;
		}

		const apiPhone = getFormattedPhoneForAPI(phone);
		if (!apiPhone) {
			toast.error($i18n.t('Please enter a valid 10-digit phone number'));
			return;
		}

		isVerifyingOtp = true;
		try {
			const sessionUser = await verifyOtp(apiPhone, otpCode, session);
			await setSessionUser(sessionUser);
			onSuccess();
		} catch (error) {
			toast.error(error || $i18n.t('Failed to verify OTP'));
		} finally {
			isVerifyingOtp = false;
		}
	};

	const handleResendOtp = async () => {
		if (countdown > 0) return;
		await handleSendOtp();
	};

	const handleOtpInput = (event) => {
		// Only allow digits and limit to 6 characters
		const value = event.target.value.replace(/\D/g, '').slice(0, 6);
		otpCode = value;
	};
</script>

<div class="w-full sm:max-w-md px-10 min-h-screen flex flex-col text-center relative">
	<!-- Centered Euron Logo Top -->
	<div class="w-full flex justify-center absolute top-4 left-0 z-10">
		<a href="https://euron.one" target="_blank" rel="noopener noreferrer" title="Visit Euron">
			<img src="https://euron-dev-thumbnails.s3.ap-south-1.amazonaws.com/logos/euron-logo-high-res.png" alt="Euron Logo" class="h-8 w-auto object-contain" />
		</a>
	</div>

	<div class="my-auto pb-10 w-full dark:text-gray-100">
		<!-- Back Button -->
		<!-- <div class="mb-6 text-left">
			<button
				class="flex items-center text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition"
				on:click={onBack}
			>
				<ArrowLeft className="w-4 h-4 mr-1" />
				{$i18n.t('Back')}
			</button>
		</div> -->

		<!-- Title -->
		<div class="mb-6">
			<div class="text-2xl font-medium">
				{$i18n.t('Sign in with OTP')}
			</div>
			<div class="mt-1 text-xs font-medium text-gray-600 dark:text-gray-500">
				{$i18n.t('Enter your phone number to receive a verification code')}
			</div>
		</div>

		{#if !otpSent}
			<!-- Phone Number Input -->
			<form
				class="flex flex-col justify-center"
				on:submit={(e) => {
					e.preventDefault();
					handleSendOtp();
				}}
			>
				<div class="mb-4">
					<label for="phone" class="text-sm font-medium text-left mb-1 block">
						{$i18n.t('Phone Number')}
					</label>
					<div class="flex items-center">
						<div class="flex items-center border border-gray-300 dark:border-gray-700 rounded-l-md bg-transparent px-3 py-2 h-11 min-w-[3.5rem] whitespace-nowrap justify-center">
							<span class="text-sm font-medium text-gray-700 dark:text-gray-300 select-none">+91</span>
						</div>
						<input
							bind:value={phone}
							on:input={handlePhoneInput}
							type="tel"
							id="phone"
							class="w-full text-sm border-t border-b border-r border-gray-300 dark:border-gray-700 rounded-r-md px-3 py-2 h-11 bg-transparent focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
							autocomplete="tel"
							placeholder={$i18n.t('Enter 10-digit phone number')}
							required
							style="font-size: 1rem;"
						/>
					</div>
					<div class="mt-1 text-xs text-gray-500 dark:text-gray-400 text-left">
						Only Indian phone numbers are allowed.
					</div>
				</div>

				<div class="mt-5">
					<button
						class="bg-gray-700/5 hover:bg-gray-700/10 dark:bg-gray-100/5 dark:hover:bg-gray-100/10 dark:text-gray-300 dark:hover:text-white transition w-full rounded-full font-medium text-sm py-2.5 disabled:opacity-50 disabled:cursor-not-allowed"
						type="submit"
						disabled={isSendingOtp || !phone || phone.replace(/\D/g, '').length !== 10}
					>
						{#if isSendingOtp}
							<Spinner />
						{:else}
							{$i18n.t('Send OTP')}
						{/if}
					</button>
				</div>
			</form>
		{:else}
			<!-- OTP Verification -->
			<form
				class="flex flex-col justify-center"
				on:submit={(e) => {
					e.preventDefault();
					handleVerifyOtp();
				}}
			>
				<div class="mb-4">
					<label for="otp" class="text-sm font-medium text-left mb-1 block">
						{$i18n.t('Verification Code')}
					</label>
					<input
						bind:value={otpCode}
						on:input={handleOtpInput}
						type="text"
						id="otp"
						class="w-full text-lg border border-gray-300 dark:border-gray-700 rounded-md px-3 py-2 bg-transparent text-center tracking-widest focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
						autocomplete="one-time-code"
						placeholder={$i18n.t('Enter 6-digit code')}
						maxlength="6"
						required
						style="font-size: 1.25rem; letter-spacing: 0.2em;"
					/>
					<div class="mt-2 text-xs text-gray-600 dark:text-gray-500">
						{$i18n.t('Code sent to')} {phone}
					</div>
				</div>

				<div class="mt-5">
					<button
						class="bg-gray-700/5 hover:bg-gray-700/10 dark:bg-gray-100/5 dark:hover:bg-gray-100/10 dark:text-gray-300 dark:hover:text-white transition w-full rounded-full font-medium text-sm py-2.5 disabled:opacity-50 disabled:cursor-not-allowed"
						type="submit"
						disabled={isVerifyingOtp || !otpCode || otpCode.length < 4}
					>
						{#if isVerifyingOtp}
							<Spinner />
						{:else}
							{$i18n.t('Verify OTP')}
						{/if}
					</button>
				</div>

				<!-- Resend OTP -->
				<div class="mt-4 text-sm text-center">
					{#if countdown > 0}
						<span class="text-gray-600 dark:text-gray-500">
							{$i18n.t('Resend code in')} {countdown}s
						</span>
					{:else}
						<button
							class="font-medium underline text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
							type="button"
							on:click={handleResendOtp}
						>
							{$i18n.t('Resend code')}
						</button>
					{/if}
				</div>

				<!-- Change Phone Number -->
				<div class="mt-2 text-sm text-center">
					<button
						class="font-medium underline text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
						type="button"
						on:click={() => {
							otpSent = false;
							otpCode = '';
							session = '';
							clearInterval(countdownInterval);
							countdown = 0;
						}}
					>
						{$i18n.t('Change phone number')}
					</button>
				</div>
			</form>
		{/if}

		<!-- Divider with Google Sign-In -->
		{#if $config?.features.external_auth_enable_google}
			<div class="mt-8">
				<div class="inline-flex items-center justify-center w-full">
					<hr class="w-32 h-px my-4 border-0 dark:bg-gray-100/10 bg-gray-700/10" />
					<span class="px-3 text-sm font-medium text-gray-900 dark:text-white bg-transparent">
						{$i18n.t('or')}
					</span>
					<hr class="w-32 h-px my-4 border-0 dark:bg-gray-100/10 bg-gray-700/10" />
				</div>
				
				<!-- Google Sign-In Component -->
				<div class="mt-4">
					<GoogleSignIn />
				</div>
			</div>
		{/if}
	</div>
</div> 