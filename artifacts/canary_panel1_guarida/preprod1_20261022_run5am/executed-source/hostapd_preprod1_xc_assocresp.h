/* Independent bench-only msg3 encoder; not an authentication mechanism.
 * Contract: preprod1_r5al_response_wire_schema_20261023.json, SHA256
 * 8c792db3ed8a71cd50c055e105091f849c22c77f700f9ea3fa52a0e9f1d311ca.
 * The caller retains all normal SSID/RSN/PSK checks and RF admission gates.
 * Uses existing hostapd crypto/utility declarations; no vendor code.
 */
#ifndef FMX_PREPROD1_XC_ASSOCRESP_H
#define FMX_PREPROD1_XC_ASSOCRESP_H

/* nonce4 is already in wire byte order; rssi2 is caller-provided metadata.
 * Return 44 on success, -1 with out unchanged on every failure.
 */
static int fmx_preprod1_xc_assocresp(u8 *out, size_t cap, const u8 *ap,
				   const u8 *xc, const u8 *nonce4,
				   const u8 *rssi2)
{
	static const u8 prefix[6] = { 0x00, 0x27, 0x22, 0xff, 0xff, 0xff };
	static const u8 bench_ap[6] = { 0x18, 0xe8, 0x29, 0x74, 0x55, 0xa2 };
	static const u8 bench_xc[6] = { 0xb4, 0xfb, 0xe4, 0x5c, 0xd5, 0xd2 };
	u8 digest[20] = { 0 }, body[32] = { 0 }, wire[44] = { 0 };
	void *aes = NULL;
	size_t pos;
	int result = -1;

	if (!out || cap < sizeof(wire) || !ap || !xc || !nonce4 || !rssi2 ||
	    os_memcmp(ap, bench_ap, 6) || os_memcmp(xc, bench_xc, 6))
		goto done;
	body[1] = 9;
	os_memcpy(body + 2, ap, 6);
	body[8] = 3;
	body[9] = 3;
	os_memcpy(body + 10, nonce4, 4);
	os_memcpy(body + 14, rssi2, 2);
	body[16] = 3; /* Empty firmware TLV, power 0, and 13 zero pad bytes. */
	wire[0] = 221;
	wire[1] = sizeof(wire) - 2;
	os_memcpy(wire + 2, prefix, sizeof(prefix));
	wire[8] = 2;
	wire[9] = 3;
	WPA_PUT_BE16(wire + 10, sizeof(body));
	/* Public addresses provide obfuscation only; WPA2 authenticates. */
	if (hmac_sha1(xc, 6, ap, 6, digest) < 0)
		goto done;
	aes = aes_encrypt_init(digest, 16);
	if (!aes)
		goto done;
	for (pos = 0; pos < sizeof(body); pos += 16) {
		if (aes_encrypt(aes, body + pos, wire + 12 + pos) < 0)
			goto done;
	}
	os_memcpy(out, wire, sizeof(wire));
	result = sizeof(wire);
done:
	if (aes)
		aes_encrypt_deinit(aes);
	forced_memzero(digest, sizeof(digest));
	forced_memzero(body, sizeof(body));
	forced_memzero(wire, sizeof(wire));
	return result;
}

#endif /* FMX_PREPROD1_XC_ASSOCRESP_H */
