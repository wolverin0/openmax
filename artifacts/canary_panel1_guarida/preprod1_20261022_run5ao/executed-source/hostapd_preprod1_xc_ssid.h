/* PREPROD1 bench interoperability experiment. Not an authentication mechanism.
 * Wire layout independently established from owned bench requests; no vendor
 * implementation code. The caller must retain normal SSID and WPA validation.
 * Uses the hostapd crypto and utility interfaces already in the build.
 */
#ifndef FMX_PREPROD1_XC_SSID_H
#define FMX_PREPROD1_XC_SSID_H

static int fmx_preprod1_xc_ssid(const u8 *ies, size_t ies_len,
			       const u8 *ap, const u8 *sa, u8 ssid[32])
{
	static const u8 prefix[6] = { 0x00, 0x27, 0x22, 0xff, 0xff, 0xff };
	static const u8 bench_ap[6] = { 0x18, 0xe8, 0x29, 0x74, 0x55, 0xa2 };
	static const u8 bench_xc[6] = { 0xb4, 0xfb, 0xe4, 0x5c, 0xd5, 0xd2 };
	const u8 *vendor = NULL;
	u8 digest[20], body[96];
	size_t pos = 0, len, end, ssid_pos, ssid_len;
	void *aes;
	int result = -1;

	if (!ies || !ap || !sa || !ssid ||
	    os_memcmp(ap, bench_ap, 6) || os_memcmp(sa, bench_xc, 6))
		return -1;
	while (pos < ies_len) {
		if (ies_len - pos < 2)
			return -1;
		len = ies[pos + 1];
		if (len > ies_len - pos - 2 || ies[pos] == 0)
			return -1;
		if (ies[pos] == 221 && len >= sizeof(prefix) &&
		    !os_memcmp(ies + pos + 2, prefix, sizeof(prefix))) {
			if (vendor || len != 106)
				return -1;
			vendor = ies + pos + 2;
		}
		pos += len + 2;
	}
	if (!vendor || vendor[6] != 2 || vendor[7] != 2 ||
	    WPA_GET_BE16(vendor + 8) != sizeof(body))
		return -1;
	/* These public addresses provide obfuscation only; WPA2 authenticates. */
	if (hmac_sha1(ap, 6, sa, 6, digest) < 0)
		return -1;
	aes = aes_decrypt_init(digest, 16);
	forced_memzero(digest, sizeof(digest));
	if (!aes)
		return -1;
	for (pos = 0; pos < sizeof(body); pos += 16) {
		if (aes_decrypt(aes, vendor + 10 + pos, body + pos) < 0)
			goto done;
	}
	if (WPA_GET_BE16(body) != 9 || os_memcmp(body + 2, sa, 6) ||
	    body[18] != 1 || body[19] == 0 || body[19] > 64)
		goto done;
	pos = 20 + body[19];
	if (pos > sizeof(body) - 2 || body[pos] != 2)
		goto done;
	ssid_len = body[pos + 1];
	ssid_pos = pos + 2;
	if (ssid_len == 0 || ssid_len > 32 ||
	    ssid_len > sizeof(body) - ssid_pos)
		goto done;
	pos = ssid_pos + ssid_len;
	/* The remaining fixed fields, single TLV3, power byte, zero padding. */
	if (pos > sizeof(body) - 9 || body[pos + 6] != 3 ||
	    body[pos + 7] > 64)
		goto done;
	end = pos + 8 + body[pos + 7];
	if (end >= sizeof(body) || sizeof(body) - end - 1 >= 16)
		goto done;
	for (pos = end + 1; pos < sizeof(body); pos++) {
		if (body[pos])
			goto done;
	}
	os_memcpy(ssid, body + ssid_pos, ssid_len);
	result = (int) ssid_len;
done:
	aes_decrypt_deinit(aes);
	forced_memzero(body, sizeof(body));
	return result;
}

#endif /* FMX_PREPROD1_XC_SSID_H */
