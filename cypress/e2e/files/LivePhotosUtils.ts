/**
 * SPDX-FileCopyrightText: 2024 Nextcloud GmbH and Nextcloud contributors
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */

import type { User } from '@nextcloud/cypress'

type SetupInfo = {
	snapshot: string
	jpgFileId: number
	movFileId: number
	fileName: string
	user: User
}

/**
 *
 * @param user
 * @param fileName
 * @param domain
 * @param requesttoken
 * @param metadata
 */
function setMetadata(user: User, fileName: string, requesttoken: string, metadata: object) {
	cy.url().then(url => {
		const hostname = new URL(url).hostname
		cy.request({
			method: 'PROPPATCH',
			url: `http://${hostname}/remote.php/dav/files/${user.userId}/${fileName}`,
			auth: { user: user.userId, pass: user.password },
			headers: {
				requesttoken,
			},
			body: `<?xml version="1.0"?>
				<d:propertyupdate xmlns:d="DAV:" xmlns:nc="http://nextcloud.org/ns">
					<d:set>
						<d:prop>
							${Object.entries(metadata).map(([key, value]) => `<${key}>${value}</${key}>`).join('\n')}
						</d:prop>
					</d:set>
				</d:propertyupdate>`,
		})
	})

}

/**
 *
 * @param enable
 */
export function setShowHiddenFiles(enable: boolean) {
	cy.get('[data-cy-files-navigation-settings-button]').click()
	// Force:true because the checkbox is hidden by the pretty UI.
	if (enable) {
		cy.get('[data-cy-files-settings-setting="show_hidden"] input').check({ force: true })
	} else {
		cy.get('[data-cy-files-settings-setting="show_hidden"] input').uncheck({ force: true })
	}
	cy.get('[data-cy-files-navigation-settings]').type('{esc}')
}

/**
 *
 */
export function setupLivePhotos(): Cypress.Chainable<SetupInfo> {
	return cy.task('getVariable', { key: 'live-photos-data' })
		.then((_setupInfo) => {
			const setupInfo = _setupInfo as SetupInfo || {}
			if (setupInfo.snapshot) {
				cy.restoreState(setupInfo.snapshot)
			} else {
				let requesttoken: string

				setupInfo.fileName = Math.random().toString(36).replace(/[^a-z]+/g, '').substring(0, 10)

				cy.createRandomUser().then(_user => { setupInfo.user = _user })

				cy.then(() => {
					cy.uploadContent(setupInfo.user, new Blob(['jpg file'], { type: 'image/jpg' }), 'image/jpg', `/${setupInfo.fileName}.jpg`)
						.then(response => { setupInfo.jpgFileId = parseInt(response.headers['oc-fileid']) })
					cy.uploadContent(setupInfo.user, new Blob(['mov file'], { type: 'video/mov' }), 'video/mov', `/${setupInfo.fileName}.mov`)
						.then(response => { setupInfo.movFileId = parseInt(response.headers['oc-fileid']) })

					cy.login(setupInfo.user)
				})

				cy.visit('/apps/files')

				cy.get('head').invoke('attr', 'data-requesttoken').then(_requesttoken => { requesttoken = _requesttoken as string })

				cy.then(() => {
					setMetadata(setupInfo.user, `${setupInfo.fileName}.jpg`, requesttoken, { 'nc:metadata-files-live-photo': setupInfo.movFileId })
					setMetadata(setupInfo.user, `${setupInfo.fileName}.mov`, requesttoken, { 'nc:metadata-files-live-photo': setupInfo.jpgFileId })
				})

				cy.then(() => {
					cy.saveState().then((value) => { setupInfo.snapshot = value })
					cy.task('setVariable', { key: 'live-photos-data', value: setupInfo })
				})
			}
			return cy.then(() => {
				cy.login(setupInfo.user)
				cy.visit('/apps/files')
				return cy.wrap(setupInfo)
			})
		})
}
