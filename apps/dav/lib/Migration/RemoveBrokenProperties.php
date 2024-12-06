<?php

/**
 * SPDX-FileCopyrightText: 2024 Nextcloud GmbH and Nextcloud contributors
 * SPDX-License-Identifier: AGPL-3.0-or-later
 */
namespace OCA\DAV\Migration;

use OCP\DB\QueryBuilder\IQueryBuilder;
use OCP\IDBConnection;
use OCP\Migration\IOutput;
use OCP\Migration\IRepairStep;

class RemoveBrokenProperties implements IRepairStep {
	private const CALENDAR_TRANSP_PROPERTY = '{urn:ietf:params:xml:ns:caldav}schedule-calendar-transp';
	
	/**
	 * RemoveBrokenProperties constructor.
	 *
	 * @param IDBConnection $db
	 */
	public function __construct(
		private IDBConnection $db,
	) {
	}

	/**
	 * @inheritdoc
	 */
	public function getName() {
		return 'Remove broken object properties';
	}

	/**
	 * @inheritdoc
	 */
	public function run(IOutput $output) {
		// select all calendar transparency properties
		$cmd = $this->db->getQueryBuilder();
		$cmd->select('id', 'propertyvalue')
			->from('properties')
			->where($cmd->expr()->eq('propertyname', $cmd->createNamedParameter(self::CALENDAR_TRANSP_PROPERTY, IQueryBuilder::PARAM_STR), IQueryBuilder::PARAM_STR));
		$result = $cmd->executeQuery();
		// find broken properties
		$brokenIds = [];
		while ($entry = $result->fetch()) {
			if (!empty($entry['propertyvalue'])) {
				$object = @unserialize(str_replace('\x00', chr(0), $entry['propertyvalue']));
				if ($object === false) {
					$brokenIds[] = $entry['id'];
				}
			} else {
				$brokenIds[] = $entry['id'];
			}
		}
		$result->closeCursor();
		// delete broken calendar transparency properties
		$cmd = $this->db->getQueryBuilder();
		$cmd->delete('properties')
			->where($cmd->expr()->in('id', $cmd->createParameter('ids'), IQueryBuilder::PARAM_STR_ARRAY));
		foreach (array_chunk($brokenIds, 1000) as $chunkIds) {
			$cmd->setParameter('ids', $chunkIds, IQueryBuilder::PARAM_STR_ARRAY);
			$cmd->executeStatement();
		}
		$total = count($brokenIds);
		$output->info("$total broken object properties removed");
	}
}
