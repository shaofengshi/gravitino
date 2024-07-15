/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *  http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
package com.datastrato.gravitino.catalog;

import static com.datastrato.gravitino.catalog.PropertiesMetadataHelpers.validatePropertyForCreate;

import com.datastrato.gravitino.EntityStore;
import com.datastrato.gravitino.NameIdentifier;
import com.datastrato.gravitino.Namespace;
import com.datastrato.gravitino.StringIdentifier;
import com.datastrato.gravitino.connector.HasPropertyMetadata;
import com.datastrato.gravitino.exceptions.FilesetAlreadyExistsException;
import com.datastrato.gravitino.exceptions.NoSuchFilesetException;
import com.datastrato.gravitino.exceptions.NoSuchSchemaException;
import com.datastrato.gravitino.exceptions.NonEmptyEntityException;
import com.datastrato.gravitino.file.Fileset;
import com.datastrato.gravitino.file.FilesetChange;
import com.datastrato.gravitino.storage.IdGenerator;
import java.util.Map;

public class FilesetOperationDispatcher extends OperationDispatcher implements FilesetDispatcher {
  /**
   * Creates a new FilesetOperationDispatcher instance.
   *
   * @param catalogManager The CatalogManager instance to be used for fileset operations.
   * @param store The EntityStore instance to be used for fileset operations.
   * @param idGenerator The IdGenerator instance to be used for fileset operations.
   */
  public FilesetOperationDispatcher(
      CatalogManager catalogManager, EntityStore store, IdGenerator idGenerator) {
    super(catalogManager, store, idGenerator);
  }

  /**
   * List the filesets in a schema namespace from the catalog.
   *
   * @param namespace A schema namespace.
   * @return An array of fileset identifiers in the namespace.
   * @throws NoSuchSchemaException If the schema does not exist.
   */
  @Override
  public NameIdentifier[] listFilesets(Namespace namespace) throws NoSuchSchemaException {
    return doWithCatalog(
        getCatalogIdentifier(NameIdentifier.of(namespace.levels())),
        c -> c.doWithFilesetOps(f -> f.listFilesets(namespace)),
        NoSuchSchemaException.class);
  }

  /**
   * Load fileset metadata by {@link NameIdentifier} from the catalog.
   *
   * @param ident A fileset identifier.
   * @return The fileset metadata.
   * @throws NoSuchFilesetException If the fileset does not exist.
   */
  @Override
  public Fileset loadFileset(NameIdentifier ident) throws NoSuchFilesetException {
    NameIdentifier catalogIdent = getCatalogIdentifier(ident);
    Fileset fileset =
        doWithCatalog(
            catalogIdent,
            c -> c.doWithFilesetOps(f -> f.loadFileset(ident)),
            NoSuchFilesetException.class);

    // Currently we only support maintaining the Fileset in the Gravitino's store.
    return EntityCombinedFileset.of(fileset)
        .withHiddenPropertiesSet(
            getHiddenPropertyNames(
                catalogIdent,
                HasPropertyMetadata::filesetPropertiesMetadata,
                fileset.properties()));
  }

  /**
   * Create a fileset metadata in the catalog.
   *
   * <p>If the type of the fileset object is "MANAGED", the underlying storageLocation can be null,
   * and Gravitino will manage the storage location based on the location of the schema.
   *
   * <p>If the type of the fileset object is "EXTERNAL", the underlying storageLocation must be set.
   *
   * @param ident A fileset identifier.
   * @param comment The comment of the fileset.
   * @param type The type of the fileset.
   * @param storageLocation The storage location of the fileset.
   * @param storageLocation2 The secondary storage location of the fileset.
   * @param properties The properties of the fileset.
   * @return The created fileset metadata
   * @throws NoSuchSchemaException If the schema does not exist.
   * @throws FilesetAlreadyExistsException If the fileset already exists.
   */
  @Override
  public Fileset createFileset(
      NameIdentifier ident,
      String comment,
      Fileset.Type type,
      String storageLocation,
      String storageLocation2,
      Map<String, String> properties)
      throws NoSuchSchemaException, FilesetAlreadyExistsException {
    NameIdentifier catalogIdent = getCatalogIdentifier(ident);
    doWithCatalog(
        catalogIdent,
        c ->
            c.doWithPropertiesMeta(
                p -> {
                  validatePropertyForCreate(p.filesetPropertiesMetadata(), properties);
                  return null;
                }),
        IllegalArgumentException.class);
    long uid = idGenerator.nextId();
    StringIdentifier stringId = StringIdentifier.fromId(uid);
    Map<String, String> updatedProperties =
        StringIdentifier.newPropertiesWithId(stringId, properties);

    Fileset createdFileset =
        doWithCatalog(
            catalogIdent,
            c ->
                c.doWithFilesetOps(
                    f ->
                        f.createFileset(
                            ident,
                            comment,
                            type,
                            storageLocation,
                            storageLocation2,
                            updatedProperties)),
            NoSuchSchemaException.class,
            FilesetAlreadyExistsException.class);
    return EntityCombinedFileset.of(createdFileset)
        .withHiddenPropertiesSet(
            getHiddenPropertyNames(
                catalogIdent,
                HasPropertyMetadata::filesetPropertiesMetadata,
                createdFileset.properties()));
  }

  /**
   * Apply the {@link FilesetChange change} to a fileset in the catalog.
   *
   * <p>Implementation may reject the change. If any change is rejected, no changes should be
   * applied to the fileset.
   *
   * <p>The {@link FilesetChange.RenameFileset} change will only update the fileset name, the
   * underlying storage location for managed fileset will not be renamed.
   *
   * @param ident A fileset identifier.
   * @param changes The changes to apply to the fileset.
   * @return The altered fileset metadata.
   * @throws NoSuchFilesetException If the fileset does not exist.
   * @throws IllegalArgumentException If the change is rejected by the implementation.
   */
  @Override
  public Fileset alterFileset(NameIdentifier ident, FilesetChange... changes)
      throws NoSuchFilesetException, IllegalArgumentException {
    validateAlterProperties(ident, HasPropertyMetadata::filesetPropertiesMetadata, changes);

    NameIdentifier catalogIdent = getCatalogIdentifier(ident);
    Fileset alteredFileset =
        doWithCatalog(
            catalogIdent,
            c -> c.doWithFilesetOps(f -> f.alterFileset(ident, changes)),
            NoSuchFilesetException.class,
            IllegalArgumentException.class);
    return EntityCombinedFileset.of(alteredFileset)
        .withHiddenPropertiesSet(
            getHiddenPropertyNames(
                catalogIdent,
                HasPropertyMetadata::filesetPropertiesMetadata,
                alteredFileset.properties()));
  }

  /**
   * Drop a fileset from the catalog.
   *
   * <p>The underlying files will be deleted if this fileset type is managed, otherwise, only the
   * metadata will be dropped.
   *
   * @param ident A fileset identifier.
   * @return true If the fileset is dropped, false the fileset did not exist.
   */
  @Override
  public boolean dropFileset(NameIdentifier ident) {
    return doWithCatalog(
        getCatalogIdentifier(ident),
        c -> c.doWithFilesetOps(f -> f.dropFileset(ident)),
        NonEmptyEntityException.class);
  }
}
