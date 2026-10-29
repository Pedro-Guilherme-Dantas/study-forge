CREATE TABLE materials (
	id UUID NOT NULL,
	source_kind VARCHAR(30) NOT NULL,
	origin_key TEXT NOT NULL,
	display_name VARCHAR(200) NOT NULL,
	original_url TEXT,
	effective_url TEXT,
	active_version_id UUID,
	status VARCHAR(20) NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE NOT NULL,
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_material_origin UNIQUE (source_kind, origin_key),
	CHECK (source_kind IN ('markdown_upload','selected_web')),
	CHECK (status IN ('processing','ready','failed','interrupted'))
);

CREATE TABLE embedding_profiles (
	id VARCHAR(200) NOT NULL,
	provider VARCHAR(30) NOT NULL,
	model VARCHAR(120) NOT NULL,
	dimensions INTEGER NOT NULL,
	configuration JSONB NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE NOT NULL,
	PRIMARY KEY (id),
	CHECK (dimensions = 768)
);

CREATE TABLE material_versions (
	id UUID NOT NULL,
	material_id UUID NOT NULL,
	version_number INTEGER NOT NULL,
	input_snapshot_text TEXT NOT NULL,
	input_sha256 VARCHAR(64) NOT NULL,
	raw_capture_sha256 VARCHAR(64) NOT NULL,
	normalized_text TEXT NOT NULL,
	normalized_sha256 VARCHAR(64),
	pipeline_fingerprint VARCHAR(64) NOT NULL,
	pipeline_config JSONB NOT NULL,
	embedding_profile_id VARCHAR(200) NOT NULL,
	expected_chunk_count INTEGER NOT NULL,
	published_chunk_count INTEGER NOT NULL,
	state VARCHAR(20) NOT NULL,
	failure_code VARCHAR(60),
	obtained_at TIMESTAMP WITH TIME ZONE,
	selected_at TIMESTAMP WITH TIME ZONE,
	created_at TIMESTAMP WITH TIME ZONE NOT NULL,
	ready_at TIMESTAMP WITH TIME ZONE,
	PRIMARY KEY (id),
	CONSTRAINT uq_version_number UNIQUE (material_id, version_number),
	CONSTRAINT uq_version_owner UNIQUE (material_id, id),
	CONSTRAINT uq_version_content UNIQUE (material_id, input_sha256, pipeline_fingerprint, embedding_profile_id),
	CHECK (state IN ('processing','ready','failed','interrupted')),
	CHECK (state <> 'ready' OR (published_chunk_count = expected_chunk_count AND expected_chunk_count > 0)),
	FOREIGN KEY(material_id) REFERENCES materials (id),
	FOREIGN KEY(embedding_profile_id) REFERENCES embedding_profiles (id)
);

CREATE INDEX ix_material_versions_state ON material_versions (state);

CREATE INDEX ix_material_versions_material_id ON material_versions (material_id);

CREATE TABLE chunks (
	id VARCHAR(64) NOT NULL,
	material_version_id UUID NOT NULL,
	ordinal INTEGER NOT NULL,
	text TEXT NOT NULL,
	start_char INTEGER NOT NULL,
	end_char INTEGER NOT NULL,
	locator JSONB NOT NULL,
	chunk_sha256 VARCHAR(64) NOT NULL,
	pipeline_fingerprint VARCHAR(64) NOT NULL,
	embedding_profile_id VARCHAR(200) NOT NULL,
	embedding VECTOR(768) NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_chunk_ordinal UNIQUE (material_version_id, ordinal),
	CHECK (end_char > start_char AND start_char >= 0),
	FOREIGN KEY(material_version_id) REFERENCES material_versions (id),
	FOREIGN KEY(embedding_profile_id) REFERENCES embedding_profiles (id)
);

CREATE INDEX ix_chunks_material_version_id ON chunks (material_version_id);

CREATE TABLE ingestion_operations (
	id UUID NOT NULL,
	material_id UUID NOT NULL,
	material_version_id UUID NOT NULL,
	state VARCHAR(20) NOT NULL,
	stage VARCHAR(20) NOT NULL,
	attempt INTEGER NOT NULL,
	error_code VARCHAR(60),
	runner_instance_id VARCHAR(36),
	created_at TIMESTAMP WITH TIME ZONE NOT NULL,
	started_at TIMESTAMP WITH TIME ZONE,
	finished_at TIMESTAMP WITH TIME ZONE,
	PRIMARY KEY (id),
	CHECK (state IN ('queued','running','succeeded','failed','interrupted')),
	CHECK (stage IN ('validate','normalize','chunk','embed','publish')),
	FOREIGN KEY(material_id) REFERENCES materials (id),
	UNIQUE (material_version_id),
	FOREIGN KEY(material_version_id) REFERENCES material_versions (id)
);

CREATE INDEX ix_ingestion_operations_material_id ON ingestion_operations (material_id);

CREATE INDEX ix_ingestion_operations_state ON ingestion_operations (state);

ALTER TABLE materials ADD CONSTRAINT fk_material_active FOREIGN KEY(id, active_version_id) REFERENCES material_versions (material_id, id);
